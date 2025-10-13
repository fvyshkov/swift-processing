import os
import subprocess
import logging
import shutil
import traceback
from datetime import datetime
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET
from apng_core.db import initDbSession, fetchall
from apng_core.exceptions import UserException

# Initialize logger
logger = logging.getLogger('cron')

# Log greeting and environment info
logger.debug('===========================================')
logger.debug('Starting SWIFT Income Processing Script')
logger.debug('🚀 VERSION: 2025-10-13 WITH MESSAGE TYPES & camt.053 PROCESSING')
logger.debug('===========================================')

# Global variables for folder paths from settings
FOLDER_IN = None
FOLDER_OUT = None

def load_settings_from_db():
    """Load settings from swift_settings table"""
    global FOLDER_IN, FOLDER_OUT

    logger.debug('Loading settings from swift_settings table...')

    sql = """
        SELECT folder_in, folder_out, server
        FROM swift_settings
        LIMIT 1
    """

    try:
        with initDbSession(database='default').cursor() as c:
            c.execute(sql)
            result = fetchall(c)

            if not result or len(result) == 0:
                raise UserException({
                    'message': 'No settings found in swift_settings table',
                    'description': 'Please configure SWIFT settings first'
                })

            settings = result[0]
            FOLDER_IN = settings.get('folder_in')
            FOLDER_OUT = settings.get('folder_out')
            server = settings.get('server')

            if not FOLDER_IN:
                raise UserException({
                    'message': 'folder_in is not configured in swift_settings',
                    'description': 'Please set folder_in in SWIFT settings'
                })

            if not FOLDER_OUT:
                raise UserException({
                    'message': 'folder_out is not configured in swift_settings',
                    'description': 'Please set folder_out in SWIFT settings'
                })

            logger.debug('='*60)
            logger.debug('SETTINGS LOADED FROM DATABASE:')
            logger.debug(f'  folder_in:  {FOLDER_IN}')
            logger.debug(f'  folder_out: {FOLDER_OUT}')
            logger.debug(f'  server:     {server or "not set"}')
            logger.debug('='*60)

            # Check and create folders
            for folder_path, folder_name in [(FOLDER_IN, 'folder_in'), (FOLDER_OUT, 'folder_out')]:
                if not os.path.exists(folder_path):
                    logger.warning(f'{folder_name} does not exist: {folder_path}')
                    logger.debug(f'Creating {folder_name}: {folder_path}')
                    try:
                        os.makedirs(folder_path, exist_ok=True)
                        logger.debug(f'✓ Created {folder_name}: {folder_path}')
                    except Exception as e:
                        raise UserException({
                            'message': f'Cannot create {folder_name}: {folder_path}',
                            'description': str(e)
                        })
                else:
                    logger.debug(f'✓ {folder_name} exists: {folder_path}')

            logger.debug('='*60)

            return FOLDER_IN

    except UserException:
        raise
    except Exception as e:
        logger.error(f'Error loading settings from database: {e}')
        raise UserException({
            'message': 'Error loading SWIFT settings from database',
            'description': str(e)
        }).withError(e)

def _find_first_by_localname(root, localname):
    """Return first element in tree by localname, ignoring namespaces."""
    for el in root.iter():
        tag = el.tag
        if isinstance(tag, str) and (tag.endswith('}' + localname) or tag == localname):
            return el
    return None

def _find_child_text_local(parent, localname):
    """Return first child text by localname under the given element (deep search)."""
    if parent is None:
        return None
    for el in parent.iter():
        if el is parent:
            continue
        tag = el.tag
        if isinstance(tag, str) and (tag.endswith('}' + localname) or tag == localname):
            txt = (el.text or '').strip()
            return txt if txt else None
    return None

def _find_all_by_localname(parent, localname):
    """Return all elements by localname under parent."""
    if parent is None:
        return []
    results = []
    for el in parent.iter():
        if el is parent:
            continue
        tag = el.tag
        if isinstance(tag, str) and (tag.endswith('}' + localname) or tag == localname):
            results.append(el)
    return results

def detect_message_type(xml_text):
    """Detect message type from MsgDefIdr in AppHdr.

    Returns: 'pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056', or None
    """
    try:
        root = ET.fromstring(xml_text)
        msg_def_idr_el = _find_first_by_localname(root, 'MsgDefIdr')

        if msg_def_idr_el is not None:
            msg_def_idr = (msg_def_idr_el.text or '').strip()
            # Extract type: "pacs.008.001.08" -> "pacs.008"
            if msg_def_idr:
                parts = msg_def_idr.split('.')
                if len(parts) >= 2:
                    msg_type = f"{parts[0]}.{parts[1]}"
                    logger.debug(f'  Detected message type: {msg_type} (from {msg_def_idr})')
                    return msg_type

        logger.debug('  Message type not detected (no MsgDefIdr found)')
        return None

    except Exception as e:
        logger.debug(f'  Error detecting message type: {e}')
        return None

def process_camt053(content, swift_input_id, cursor):
    """Process camt.053 statement and insert balances, entries, and transaction details.

    Args:
        content: XML content as string
        swift_input_id: UUID of the swift_input record
        cursor: Database cursor

    Returns:
        dict with counts: {'balances': N, 'entries': N, 'tx_details': N}
    """
    logger.debug(f'  Processing camt.053 for swift_input_id={swift_input_id}')

    counts = {'balances': 0, 'entries': 0, 'tx_details': 0}

    try:
        root = ET.fromstring(content)

        # Find Stmt element
        stmt = _find_first_by_localname(root, 'Stmt')
        if stmt is None:
            logger.warning('  No Stmt element found in camt.053')
            return counts

        # Process Balances (Bal)
        bal_elements = _find_all_by_localname(stmt, 'Bal')
        logger.debug(f'  Found {len(bal_elements)} balance(s)')

        for bal_el in bal_elements:
            try:
                # Extract balance type
                tp_cd_el = _find_first_by_localname(bal_el, 'Cd')
                tp_cd = (tp_cd_el.text or '').strip() if tp_cd_el is not None else None

                # Extract amount
                amt_el = _find_first_by_localname(bal_el, 'Amt')
                if amt_el is None:
                    continue

                amt_text = (amt_el.text or '').strip()
                amt_ccy = amt_el.attrib.get('Ccy')

                try:
                    amt = Decimal(amt_text)
                except:
                    amt = None

                # Extract credit/debit indicator
                cdt_dbt_ind_el = _find_first_by_localname(bal_el, 'CdtDbtInd')
                cdt_dbt_ind = (cdt_dbt_ind_el.text or '').strip() if cdt_dbt_ind_el is not None else None

                # Extract date
                dt_el = _find_first_by_localname(bal_el, 'Dt')
                dt_text = (dt_el.text or '').strip() if dt_el is not None else None

                # Insert balance
                if tp_cd and amt is not None and cdt_dbt_ind and dt_text:
                    cursor.execute("""
                        INSERT INTO swift_stmt_bal
                        (swift_input_id, tp_cd, amt, amt_ccy, cdt_dbt_ind, dt)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (swift_input_id, tp_cd, amt, amt_ccy, cdt_dbt_ind, dt_text))
                    counts['balances'] += 1
                    logger.debug(f'    Inserted balance: {tp_cd} = {amt} {amt_ccy} ({cdt_dbt_ind})')

            except Exception as bal_err:
                logger.error(f'    Error processing balance: {bal_err}')
                continue

        # Process Entries (Ntry)
        ntry_elements = _find_all_by_localname(stmt, 'Ntry')
        logger.debug(f'  Found {len(ntry_elements)} entry/entries')

        for ntry_el in ntry_elements:
            try:
                # Extract entry fields
                ntry_ref = _find_child_text_local(ntry_el, 'NtryRef')
                acct_svcr_ref = _find_child_text_local(ntry_el, 'AcctSvcrRef')

                # Amount
                amt_el = _find_first_by_localname(ntry_el, 'Amt')
                if amt_el is None:
                    continue

                amt_text = (amt_el.text or '').strip()
                amt_ccy = amt_el.attrib.get('Ccy')

                try:
                    amt = Decimal(amt_text)
                except:
                    amt = None

                if amt is None:
                    continue

                # Credit/Debit indicator
                cdt_dbt_ind_el = _find_first_by_localname(ntry_el, 'CdtDbtInd')
                cdt_dbt_ind = (cdt_dbt_ind_el.text or '').strip() if cdt_dbt_ind_el is not None else 'CRDT'

                # Status
                sts_cd_el = _find_first_by_localname(ntry_el, 'Cd')
                # Find Sts/Cd specifically
                sts_parent = _find_first_by_localname(ntry_el, 'Sts')
                if sts_parent:
                    sts_cd_el = _find_first_by_localname(sts_parent, 'Cd')
                sts_cd = (sts_cd_el.text or '').strip() if sts_cd_el is not None else 'BOOK'

                # Dates
                bookg_dt_el = _find_first_by_localname(ntry_el, 'BookgDt')
                bookg_dt = None
                if bookg_dt_el:
                    dt_sub = _find_first_by_localname(bookg_dt_el, 'Dt')
                    if dt_sub is not None:
                        bookg_dt = (dt_sub.text or '').strip()

                val_dt_el = _find_first_by_localname(ntry_el, 'ValDt')
                val_dt = None
                if val_dt_el:
                    dt_sub = _find_first_by_localname(val_dt_el, 'Dt')
                    if dt_sub is not None:
                        val_dt = (dt_sub.text or '').strip()

                # Bank Transaction Code
                bk_tx_cd = _find_first_by_localname(ntry_el, 'BkTxCd')
                bk_tx_cd_domn_cd = None
                bk_tx_cd_fmly_cd = None
                bk_tx_cd_sub_fmly_cd = None

                if bk_tx_cd:
                    domn = _find_first_by_localname(bk_tx_cd, 'Domn')
                    if domn:
                        cd_el = _find_first_by_localname(domn, 'Cd')
                        bk_tx_cd_domn_cd = (cd_el.text or '').strip() if cd_el is not None else None

                        fmly = _find_first_by_localname(domn, 'Fmly')
                        if fmly:
                            cd_el = _find_first_by_localname(fmly, 'Cd')
                            bk_tx_cd_fmly_cd = (cd_el.text or '').strip() if cd_el is not None else None

                            sub_el = _find_first_by_localname(fmly, 'SubFmlyCd')
                            bk_tx_cd_sub_fmly_cd = (sub_el.text or '').strip() if sub_el is not None else None

                # Insert entry
                cursor.execute("""
                    INSERT INTO swift_stmt_ntry
                    (swift_input_id, ntry_ref, acct_svcr_ref, amt, amt_ccy, cdt_dbt_ind,
                     sts_cd, bookg_dt, val_dt, bk_tx_cd_domn_cd, bk_tx_cd_fmly_cd, bk_tx_cd_sub_fmly_cd)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (swift_input_id, ntry_ref, acct_svcr_ref, amt, amt_ccy, cdt_dbt_ind,
                      sts_cd, bookg_dt, val_dt, bk_tx_cd_domn_cd, bk_tx_cd_fmly_cd, bk_tx_cd_sub_fmly_cd))

                ntry_id_result = cursor.fetchone()
                if isinstance(ntry_id_result, dict):
                    ntry_id = ntry_id_result.get('id')
                elif isinstance(ntry_id_result, (list, tuple)):
                    ntry_id = ntry_id_result[0]
                else:
                    ntry_id = ntry_id_result

                counts['entries'] += 1
                logger.debug(f'    Inserted entry: ntry_id={ntry_id}, amt={amt} {amt_ccy}, status={sts_cd}')

                # Process Transaction Details (TxDtls)
                ntry_dtls = _find_first_by_localname(ntry_el, 'NtryDtls')
                if ntry_dtls:
                    tx_dtls_elements = _find_all_by_localname(ntry_dtls, 'TxDtls')
                    logger.debug(f'      Found {len(tx_dtls_elements)} transaction detail(s)')

                    for tx_dtls_el in tx_dtls_elements:
                        try:
                            # References
                            refs = _find_first_by_localname(tx_dtls_el, 'Refs')
                            instr_id = None
                            end_to_end_id = None
                            uetr = None

                            if refs:
                                instr_id = _find_child_text_local(refs, 'InstrId')
                                end_to_end_id = _find_child_text_local(refs, 'EndToEndId')
                                uetr_text = _find_child_text_local(refs, 'UETR')
                                if uetr_text:
                                    try:
                                        # Validate UUID format
                                        import uuid
                                        uuid.UUID(uetr_text)
                                        uetr = uetr_text
                                    except:
                                        uetr = None

                            # Amount
                            tx_amt_el = _find_first_by_localname(tx_dtls_el, 'Amt')
                            tx_amt = None
                            tx_amt_ccy = None
                            if tx_amt_el is not None:
                                tx_amt_text = (tx_amt_el.text or '').strip()
                                tx_amt_ccy = tx_amt_el.attrib.get('Ccy')
                                try:
                                    tx_amt = Decimal(tx_amt_text)
                                except:
                                    pass

                            # Credit/Debit
                            tx_cdt_dbt_ind_el = _find_first_by_localname(tx_dtls_el, 'CdtDbtInd')
                            tx_cdt_dbt_ind = (tx_cdt_dbt_ind_el.text or '').strip() if tx_cdt_dbt_ind_el is not None else None

                            # Related dates
                            rltd_dts = _find_first_by_localname(tx_dtls_el, 'RltdDts')
                            intr_bk_sttlm_dt = None
                            if rltd_dts:
                                dt_el = _find_first_by_localname(rltd_dts, 'IntrBkSttlmDt')
                                intr_bk_sttlm_dt = (dt_el.text or '').strip() if dt_el is not None else None

                            # Insert transaction detail
                            cursor.execute("""
                                INSERT INTO swift_entry_tx_dtls
                                (ntry_id, instr_id, end_to_end_id, uetr, amt, amt_ccy,
                                 cdt_dbt_ind, intr_bk_sttlm_dt)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (ntry_id, instr_id, end_to_end_id, uetr, tx_amt, tx_amt_ccy,
                                  tx_cdt_dbt_ind, intr_bk_sttlm_dt))

                            counts['tx_details'] += 1
                            logger.debug(f'        Inserted tx_detail: end_to_end={end_to_end_id}, amt={tx_amt}')

                        except Exception as tx_err:
                            logger.error(f'        Error processing transaction detail: {tx_err}')
                            continue

            except Exception as ntry_err:
                logger.error(f'    Error processing entry: {ntry_err}')
                continue

        logger.debug(f'  camt.053 processing complete: {counts["balances"]} balances, {counts["entries"]} entries, {counts["tx_details"]} tx_details')
        return counts

    except Exception as e:
        logger.error(f'  Error processing camt.053: {e}')
        logger.error(f'  Traceback: {traceback.format_exc()}')
        return counts

def extract_pacs008_fields(xml_text):
    """Extract sender, receiver, amount, date, currency and additional fields from pacs.008 XML.

    Returns dict with keys: snd_name, rcv_name, amount, currency_code, dval, code, message,
    snd_acc, rcv_acc, snd_bank, snd_bank_name, snd_mid_bank, snd_mid_bank_name,
    snd_mid_bank_acc, rcv_bank, rcv_bank_name, error.
    """
    result = {
        'snd_name': None,
        'rcv_name': None,
        'amount': None,
        'currency_code': None,
        'dval': None,
        'code': None,
        'message': None,
        'snd_acc': None,
        'rcv_acc': None,
        'snd_bank': None,
        'snd_bank_name': None,
        'snd_mid_bank': None,
        'snd_mid_bank_name': None,
        'snd_mid_bank_acc': None,
        'rcv_bank': None,
        'rcv_bank_name': None,
        'error': None,
    }

    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = f'XML parse error: {e}\\n\\nTraceback:\\n{tb}'
        return result

    # Debtor (sender name)
    try:
        dbtr = _find_first_by_localname(root, 'Dbtr')
        result['snd_name'] = _find_child_text_local(dbtr, 'Nm')
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | sender parse error: {e}\\nTraceback:\\n{tb}'

    # Creditor (receiver name)
    try:
        cdtr = _find_first_by_localname(root, 'Cdtr')
        result['rcv_name'] = _find_child_text_local(cdtr, 'Nm')
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | receiver parse error: {e}\\nTraceback:\\n{tb}'

    # Amount and currency
    try:
        amt_el = _find_first_by_localname(root, 'IntrBkSttlmAmt')
        if amt_el is not None:
            val_text = (amt_el.text or '').strip()
            try:
                result['amount'] = Decimal(val_text)
            except (InvalidOperation, ValueError):
                result['amount'] = None
                if val_text:
                    result['error'] = (result['error'] or '') + f' | bad amount: {val_text}'
            result['currency_code'] = amt_el.attrib.get('Ccy')
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | amount parse error: {e}\\nTraceback:\\n{tb}'

    # Value date
    try:
        dval_el = _find_first_by_localname(root, 'IntrBkSttlmDt')
        if dval_el is not None and (dval_el.text or '').strip():
            result['dval'] = (dval_el.text or '').strip()
        else:
            cre_el = _find_first_by_localname(root, 'CreDtTm')
            if cre_el is not None and (cre_el.text or '').strip():
                result['dval'] = (cre_el.text or '').strip()[:10]
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | date parse error: {e}\\nTraceback:\\n{tb}'

    # Code (EndToEndId or InstrId)
    try:
        code_el = _find_first_by_localname(root, 'EndToEndId')
        if code_el is not None and (code_el.text or '').strip():
            result['code'] = (code_el.text or '').strip()
        else:
            instr_el = _find_first_by_localname(root, 'InstrId')
            if instr_el is not None:
                result['code'] = (instr_el.text or '').strip()
    except Exception as e:
        pass

    # Message (Remittance Information)
    try:
        ustrd_el = _find_first_by_localname(root, 'Ustrd')
        if ustrd_el is not None:
            result['message'] = (ustrd_el.text or '').strip()
    except Exception as e:
        pass

    # Sender account
    try:
        dbtr_acct = _find_first_by_localname(root, 'DbtrAcct')
        if dbtr_acct is not None:
            iban_el = _find_child_text_local(dbtr_acct, 'IBAN')
            if iban_el:
                result['snd_acc'] = iban_el
            else:
                othr_id = _find_child_text_local(dbtr_acct, 'Id')
                if othr_id:
                    result['snd_acc'] = othr_id
    except Exception as e:
        pass

    # Receiver account
    try:
        cdtr_acct = _find_first_by_localname(root, 'CdtrAcct')
        if cdtr_acct is not None:
            iban_el = _find_child_text_local(cdtr_acct, 'IBAN')
            if iban_el:
                result['rcv_acc'] = iban_el
            else:
                othr_id = _find_child_text_local(cdtr_acct, 'Id')
                if othr_id:
                    result['rcv_acc'] = othr_id
    except Exception as e:
        pass

    # Sender bank
    try:
        dbtr_agt = _find_first_by_localname(root, 'DbtrAgt')
        if dbtr_agt is not None:
            bic_el = _find_child_text_local(dbtr_agt, 'BICFI')
            if bic_el:
                result['snd_bank'] = bic_el
            name_el = _find_child_text_local(dbtr_agt, 'Nm')
            if name_el:
                result['snd_bank_name'] = name_el
    except Exception as e:
        pass

    # Receiver bank
    try:
        cdtr_agt = _find_first_by_localname(root, 'CdtrAgt')
        if cdtr_agt is not None:
            bic_el = _find_child_text_local(cdtr_agt, 'BICFI')
            if bic_el:
                result['rcv_bank'] = bic_el
            name_el = _find_child_text_local(cdtr_agt, 'Nm')
            if name_el:
                result['rcv_bank_name'] = name_el
    except Exception as e:
        pass

    # Intermediary bank
    try:
        instg_agt = _find_first_by_localname(root, 'InstgAgt')
        if instg_agt is not None:
            bic_el = _find_child_text_local(instg_agt, 'BICFI')
            if bic_el:
                result['snd_mid_bank'] = bic_el
            name_el = _find_child_text_local(instg_agt, 'Nm')
            if name_el:
                result['snd_mid_bank_name'] = name_el
            clr_sys = _find_child_text_local(instg_agt, 'MmbId')
            if clr_sys:
                result['snd_mid_bank_acc'] = clr_sys
    except Exception as e:
        pass

    if not any([result['snd_name'], result['rcv_name'], result['amount'], result['currency_code'], result['dval']]):
        result['error'] = result['error'] or 'No key fields extracted'

    return result

def create_test_file():
    """Create test files in the folder_in directory"""
    global FOLDER_IN
    logger.debug(f'create_test_file: Starting with path {FOLDER_IN}')

    # Check if directory exists
    try:
        if not os.path.exists(FOLDER_IN):
            logger.debug(f'Directory {FOLDER_IN} does not exist, creating it...')
            os.makedirs(FOLDER_IN, exist_ok=True)
            logger.debug(f'Directory created: {FOLDER_IN}')
        else:
            logger.debug(f'Directory exists: {FOLDER_IN}')

        # CLEAN DIRECTORY
        try:
            contents_before = os.listdir(FOLDER_IN)
            if contents_before:
                logger.debug(f'Cleaning directory: found {len(contents_before)} files to remove')
                for filename in contents_before:
                    file_path = os.path.join(FOLDER_IN, filename)
                    if os.path.isfile(file_path):
                        try:
                            os.remove(file_path)
                            logger.debug(f'  Removed: {filename}')
                        except Exception as e:
                            logger.error(f'  Error removing {filename}: {e}')
                logger.debug('Directory cleaned successfully')
            else:
                logger.debug('Directory is already empty')
        except Exception as e:
            logger.error(f'Cannot clean directory: {e}')

        # Check if directory is writable
        if not os.access(FOLDER_IN, os.W_OK):
            logger.error(f'Input directory is not writable: {FOLDER_IN}')
            raise UserException({
                'message': 'Input directory is not writable',
                'description': f'Path: {FOLDER_IN}'
            })
        else:
            logger.debug(f'Directory is writable')
    except Exception as e:
        logger.error(f'Error checking/creating input directory: {e}')
        raise UserException({
            'message': 'Error checking/creating input directory',
            'description': f'Path: {FOLDER_IN}'
        }).withError(e)

    # Create pacs.008 XML example file
    logger.debug('Creating pacs.008 XML test file...')
    pacs008_file_path = os.path.join(FOLDER_IN, 'pacs008_example.xml')
    try:
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="urn:swift:xsd:envelope">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:Fr><head:FIId><head:FinInstnId><head:BICFI>DSBAHKHH</head:BICFI></head:FinInstnId></head:FIId></head:Fr>
		<head:To><head:FIId><head:FinInstnId><head:BICFI>ID521122</head:BICFI></head:FinInstnId></head:FIId></head:To>
		<head:BizMsgIdr>pacs8bizmsgidr02</head:BizMsgIdr>
		<head:MsgDefIdr>pacs.008.001.08</head:MsgDefIdr>
		<head:BizSvc>swift.cbprplus.02</head:BizSvc>
		<head:CreDt>2022-10-20T10:25:00+01:00</head:CreDt>
	</head:AppHdr>
	<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
		<pacs:FIToFICstmrCdtTrf>
			<pacs:GrpHdr><pacs:MsgId>pacs8bizmsgidr02</pacs:MsgId><pacs:CreDtTm>2022-10-20T10:25:00+01:00</pacs:CreDtTm><pacs:NbOfTxs>1</pacs:NbOfTxs><pacs:SttlmInf><pacs:SttlmMtd>INDA</pacs:SttlmMtd></pacs:SttlmInf></pacs:GrpHdr>
			<pacs:CdtTrfTxInf>
				<pacs:PmtId><pacs:InstrId>pacs8bizmsgidr02</pacs:InstrId><pacs:EndToEndId>pacs008EndToEndId-001</pacs:EndToEndId><pacs:UETR>7a562c67-ca16-48ba-b074-65581be6f001</pacs:UETR></pacs:PmtId>
				<pacs:IntrBkSttlmAmt Ccy="USD">98725497</pacs:IntrBkSttlmAmt>
				<pacs:IntrBkSttlmDt>2022-10-20</pacs:IntrBkSttlmDt>
				<pacs:Dbtr><pacs:Nm>A Capone</pacs:Nm></pacs:Dbtr>
				<pacs:DbtrAcct><pacs:Id><pacs:Othr><pacs:Id>ACPN-2569874</pacs:Id></pacs:Othr></pacs:Id></pacs:DbtrAcct>
				<pacs:Cdtr><pacs:Nm>J Smith</pacs:Nm></pacs:Cdtr>
				<pacs:CdtrAcct><pacs:Id><pacs:Othr><pacs:Id>65479512</pacs:Id></pacs:Othr></pacs:Id></pacs:CdtrAcct>
			</pacs:CdtTrfTxInf>
		</pacs:FIToFICstmrCdtTrf>
	</pacs:Document>
</Envelope>'''
        with open(pacs008_file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        logger.debug(f'Successfully created pacs.008 XML file: {pacs008_file_path}')
    except Exception as e:
        logger.error(f'Error creating pacs.008 XML file: {e}')

    # Create camt.053 XML example file
    logger.debug('Creating camt.053 XML test file...')
    camt053_file_path = os.path.join(FOLDER_IN, 'camt053_example.xml')
    try:
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="urn:swift:xsd:envelope">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:Fr><head:FIId><head:FinInstnId><head:BICFI>DNBANOKK</head:BICFI></head:FinInstnId></head:FIId></head:Fr>
		<head:To><head:FIId><head:FinInstnId><head:BICFI>GUCRNOK1</head:BICFI></head:FinInstnId></head:FIId></head:To>
		<head:BizMsgIdr>cmt053bizmsgidr-001</head:BizMsgIdr>
		<head:MsgDefIdr>camt.053.001.08</head:MsgDefIdr>
		<head:BizSvc>swift.cbprplus.02</head:BizSvc>
		<head:CreDt>2021-06-03T18:00:00+02:00</head:CreDt>
	</head:AppHdr>
	<camt:Document xmlns:camt="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
		<camt:BkToCstmrStmt>
			<camt:GrpHdr><camt:MsgId>cmt053bizmsgidr-001</camt:MsgId><camt:CreDtTm>2021-06-03T18:00:00+02:00</camt:CreDtTm></camt:GrpHdr>
			<camt:Stmt>
				<camt:Id>STMNTID</camt:Id>
				<camt:StmtPgntn><camt:PgNb>1</camt:PgNb><camt:LastPgInd>true</camt:LastPgInd></camt:StmtPgntn>
				<camt:ElctrncSeqNb>32145</camt:ElctrncSeqNb>
				<camt:Acct><camt:Id><camt:Othr><camt:Id>123654786</camt:Id></camt:Othr></camt:Id><camt:Ccy>NOK</camt:Ccy></camt:Acct>
				<camt:Bal>
					<camt:Tp><camt:CdOrPrtry><camt:Cd>OPBD</camt:Cd></camt:CdOrPrtry></camt:Tp>
					<camt:Amt Ccy="NOK">4645498.54</camt:Amt>
					<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
					<camt:Dt><camt:Dt>2021-06-03</camt:Dt></camt:Dt>
				</camt:Bal>
				<camt:Bal>
					<camt:Tp><camt:CdOrPrtry><camt:Cd>CLBD</camt:Cd></camt:CdOrPrtry></camt:Tp>
					<camt:Amt Ccy="NOK">7010498.54</camt:Amt>
					<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
					<camt:Dt><camt:Dt>2021-06-03</camt:Dt></camt:Dt>
				</camt:Bal>
				<camt:Ntry>
					<camt:Amt Ccy="NOK">2365000</camt:Amt>
					<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
					<camt:Sts><camt:Cd>BOOK</camt:Cd></camt:Sts>
					<camt:BookgDt><camt:Dt>2021-06-03</camt:Dt></camt:BookgDt>
					<camt:ValDt><camt:Dt>2021-06-03</camt:Dt></camt:ValDt>
					<camt:BkTxCd><camt:Domn><camt:Cd>PMNT</camt:Cd><camt:Fmly><camt:Cd>RCDT</camt:Cd><camt:SubFmlyCd>XBCT</camt:SubFmlyCd></camt:Fmly></camt:Domn></camt:BkTxCd>
					<camt:NtryDtls>
						<camt:TxDtls>
							<camt:Refs><camt:InstrId>pacs8bizmsgidr01</camt:InstrId><camt:EndToEndId>E2E04044506271305</camt:EndToEndId><camt:UETR>174c245f-2682-4291-ad67-2a41e530cd27</camt:UETR></camt:Refs>
							<camt:Amt Ccy="NOK">2365000</camt:Amt>
							<camt:CdtDbtInd>CRDT</camt:CdtDbtInd>
						</camt:TxDtls>
					</camt:NtryDtls>
				</camt:Ntry>
			</camt:Stmt>
		</camt:BkToCstmrStmt>
	</camt:Document>
</Envelope>'''
        with open(camt053_file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        logger.debug(f'Successfully created camt.053 XML file: {camt053_file_path}')
    except Exception as e:
        logger.error(f'Error creating camt.053 XML file: {e}')

    # Create error test file
    logger.debug('Creating error test file...')
    error_test_file_path = os.path.join(FOLDER_IN, 'error_test.xml')
    try:
        with open(error_test_file_path, 'w', encoding='utf-8') as f:
            f.write('sample error file')
        logger.debug(f'Successfully created error test file: {error_test_file_path}')
    except Exception as e:
        logger.error(f'Error creating error test file: {e}')

    # List contents
    try:
        contents_after = os.listdir(FOLDER_IN)
        logger.debug(f'Files AFTER creating test files: {len(contents_after)} files')
        for filename in contents_after:
            file_path = os.path.join(FOLDER_IN, filename)
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
            logger.debug(f'  - {filename} ({size} bytes)')
    except Exception as e:
        logger.error(f'Cannot list directory: {e}')

def read_and_import_files():
    """Read all files from folder_in directory and import to swift_input table"""
    global FOLDER_IN
    logger.debug(f'read_and_import_files: Starting with path {FOLDER_IN}')

    if not os.path.exists(FOLDER_IN):
        logger.error(f'Input directory not found: {FOLDER_IN}')
        raise UserException({
            'message': 'Input directory not found',
            'description': f'Path: {FOLDER_IN}'
        })

    # Get all files
    try:
        files = [f for f in os.listdir(FOLDER_IN) if os.path.isfile(os.path.join(FOLDER_IN, f))]
        logger.debug(f'Found {len(files)} files in {FOLDER_IN}')
        if files:
            logger.debug(f'Files to process:')
            for filename in files:
                file_path = os.path.join(FOLDER_IN, filename)
                size = os.path.getsize(file_path)
                logger.debug(f'  - {filename} ({size} bytes)')
        else:
            logger.warning('No files found in directory!')
            return 0
    except Exception as e:
        logger.error(f'Error reading input directory: {e}')
        raise UserException({
            'message': 'Error reading input directory',
            'description': f'Path: {FOLDER_IN}'
        }).withError(e)

    imported_count = 0
    skipped_count = 0
    error_count = 0

    with initDbSession(database='default').cursor() as c:
        for filename in files:
            file_path = os.path.join(FOLDER_IN, filename)
            logger.debug(f'Processing file: {filename}')

            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                logger.debug(f'  File size: {len(content)} bytes')

                current_date = datetime.now()

                # Detect message type
                msg_type = detect_message_type(content)

                # Check if message type is in our list
                supported_types = ['pacs.008', 'pacs.009', 'camt.053', 'camt.054', 'camt.056']

                if msg_type not in supported_types:
                    # Unknown or unsupported message type - only copy to folder_out
                    logger.warning(f'  Message type {msg_type} is not supported, skipping DB insert')
                    skipped_count += 1

                    # Copy to folder_out
                    dest_file_path = os.path.join(FOLDER_OUT, filename)
                    try:
                        shutil.copy2(file_path, dest_file_path)
                        logger.debug(f'  Copied file to: {dest_file_path}')
                    except Exception as copy_err:
                        logger.error(f'  Error copying file: {copy_err}')

                    continue

                # Process supported message types
                logger.debug(f'  Processing as {msg_type}')

                # Extract fields based on message type
                if msg_type in ['pacs.008', 'pacs.009']:
                    fields = extract_pacs008_fields(content)
                    state_value = 'finished' if not fields.get('error') else 'error'

                    # Insert into swift_input
                    insert_sql = """
                        INSERT INTO swift_input (
                            file_name, state, content, imported, msg_type,
                            snd_name, rcv_name, amount, currency_code, dval,
                            code, message, snd_acc, rcv_acc,
                            snd_bank, snd_bank_name, snd_mid_bank, snd_mid_bank_name, snd_mid_bank_acc,
                            rcv_bank, rcv_bank_name, error
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    c.execute(insert_sql, (
                        filename, state_value, content, current_date, msg_type,
                        fields.get('snd_name'), fields.get('rcv_name'),
                        fields.get('amount'), fields.get('currency_code'), fields.get('dval'),
                        fields.get('code'), fields.get('message'),
                        fields.get('snd_acc'), fields.get('rcv_acc'),
                        fields.get('snd_bank'), fields.get('snd_bank_name'),
                        fields.get('snd_mid_bank'), fields.get('snd_mid_bank_name'), fields.get('snd_mid_bank_acc'),
                        fields.get('rcv_bank'), fields.get('rcv_bank_name'),
                        fields.get('error')
                    ))
                    imported_count += 1
                    logger.debug(f'  Successfully imported {msg_type} file: {filename}')

                elif msg_type == 'camt.053':
                    # Extract basic info
                    root = ET.fromstring(content)

                    # Extract MsgId and StmtId
                    msg_id_el = _find_first_by_localname(root, 'MsgId')
                    msg_id = (msg_id_el.text or '').strip() if msg_id_el is not None else None

                    stmt_el = _find_first_by_localname(root, 'Stmt')
                    stmt_id = None
                    elctrnc_seq_nb = None
                    acct_id = None
                    acct_ccy = None

                    if stmt_el:
                        id_el = _find_first_by_localname(stmt_el, 'Id')
                        stmt_id = (id_el.text or '').strip() if id_el is not None else None

                        seq_el = _find_first_by_localname(stmt_el, 'ElctrncSeqNb')
                        elctrnc_seq_nb_text = (seq_el.text or '').strip() if seq_el is not None else None
                        if elctrnc_seq_nb_text:
                            try:
                                elctrnc_seq_nb = int(elctrnc_seq_nb_text)
                            except:
                                pass

                        acct_el = _find_first_by_localname(stmt_el, 'Acct')
                        if acct_el:
                            acct_id_el = _find_first_by_localname(acct_el, 'Id')
                            if acct_id_el:
                                othr = _find_first_by_localname(acct_id_el, 'Othr')
                                if othr:
                                    id_sub = _find_first_by_localname(othr, 'Id')
                                    acct_id = (id_sub.text or '').strip() if id_sub is not None else None

                            ccy_el = _find_first_by_localname(acct_el, 'Ccy')
                            acct_ccy = (ccy_el.text or '').strip() if ccy_el is not None else None

                    # Insert into swift_input
                    insert_sql = """
                        INSERT INTO swift_input (
                            file_name, state, content, imported, msg_type,
                            msg_id, stmt_id, elctrnc_seq_nb, acct_id, acct_ccy
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    c.execute(insert_sql, (
                        filename, 'finished', content, current_date, msg_type,
                        msg_id, stmt_id, elctrnc_seq_nb, acct_id, acct_ccy
                    ))

                    # Get swift_input_id
                    result = c.fetchone()
                    if isinstance(result, dict):
                        swift_input_id = result.get('id')
                    elif isinstance(result, (list, tuple)):
                        swift_input_id = result[0]
                    else:
                        swift_input_id = result

                    logger.debug(f'  Inserted swift_input record: id={swift_input_id}')

                    # Process camt.053 details
                    counts = process_camt053(content, swift_input_id, c)

                    imported_count += 1
                    logger.debug(f'  Successfully imported camt.053 file: {filename}')

                elif msg_type in ['camt.054', 'camt.056']:
                    # Basic insert for future processing
                    insert_sql = """
                        INSERT INTO swift_input (
                            file_name, state, content, imported, msg_type
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    c.execute(insert_sql, (filename, 'finished', content, current_date, msg_type))
                    imported_count += 1
                    logger.debug(f'  Successfully imported {msg_type} file: {filename}')

                # Copy to folder_out
                dest_file_path = os.path.join(FOLDER_OUT, filename)
                try:
                    shutil.copy2(file_path, dest_file_path)
                    logger.debug(f'  Copied file to: {dest_file_path}')
                except Exception as copy_err:
                    logger.error(f'  Error copying file: {copy_err}')

            except UnicodeDecodeError:
                error_msg = 'UTF-8 decode failed'
                logger.error(f'  {error_msg} for {filename}')
                error_count += 1

                try:
                    dest_file_path = os.path.join(FOLDER_OUT, filename)
                    shutil.copy2(file_path, dest_file_path)

                    error_file_path = os.path.join(FOLDER_OUT, f'{filename}.error.txt')
                    with open(error_file_path, 'w', encoding='utf-8') as err_f:
                        err_f.write(f'Error processing file: {filename}\\n')
                        err_f.write(f'Timestamp: {datetime.now()}\\n')
                        err_f.write(f'\\nError: {error_msg}\\n')
                except:
                    pass
                continue

            except Exception as e:
                logger.error(f'  Error processing file {filename}: {str(e)}')
                logger.error(f'  Traceback: {traceback.format_exc()}')
                error_count += 1

                try:
                    dest_file_path = os.path.join(FOLDER_OUT, filename)
                    shutil.copy2(file_path, dest_file_path)

                    error_file_path = os.path.join(FOLDER_OUT, f'{filename}.error.txt')
                    tb = traceback.format_exc()
                    with open(error_file_path, 'w', encoding='utf-8') as err_f:
                        err_f.write(f'Error processing file: {filename}\\n')
                        err_f.write(f'Timestamp: {datetime.now()}\\n')
                        err_f.write(f'\\nError: {str(e)}\\n\\nTraceback:\\n{tb}')
                except:
                    pass
                continue

        # Commit transaction
        if imported_count > 0:
            c.connection.commit()
            logger.debug(f'Transaction committed: {imported_count} files')

    logger.debug('='*60)
    logger.debug(f'IMPORT SUMMARY:')
    logger.debug(f'  Imported: {imported_count} files')
    logger.debug(f'  Skipped (unknown type): {skipped_count} files')
    logger.debug(f'  Errors: {error_count} files')
    logger.debug(f'  All files copied to: {FOLDER_OUT}')
    logger.debug('='*60)

    return imported_count

def main():
    """Main execution function"""
    global FOLDER_IN

    try:
        # Load settings
        load_settings_from_db()

        logger.debug('='*80)
        logger.debug('main: Starting SWIFT import process')
        logger.debug(f'Input folder: {FOLDER_IN}')
        logger.debug('='*80)

        # Create test files
        logger.debug('Step 1: Creating test files...')
        create_test_file()

        # Read and import files
        logger.debug('Step 2: Reading and importing files...')
        imported_count = read_and_import_files()

        logger.debug('='*80)
        logger.debug('Process completed successfully!')
        logger.debug(f'Total files imported: {imported_count}')
        logger.debug('='*80)

    except UserException as e:
        logger.error(f'User error: {e}')
        raise
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise UserException({
            'message': 'Unexpected error in main process',
            'description': str(e)
        }).withError(e)

main()
