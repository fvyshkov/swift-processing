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
logger.debug('🚀 VERSION: 2025-10-10-13:00 WITH CLEANING & PACS008 XML')
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
            
            # Check and create folder_in if needed
            if not os.path.exists(FOLDER_IN):
                logger.warning(f'folder_in does not exist: {FOLDER_IN}')
                logger.debug(f'Creating folder_in: {FOLDER_IN}')
                try:
                    os.makedirs(FOLDER_IN, exist_ok=True)
                    logger.debug(f'✓ Created folder_in: {FOLDER_IN}')
                except Exception as e:
                    raise UserException({
                        'message': f'Cannot create folder_in: {FOLDER_IN}',
                        'description': str(e)
                    })
            else:
                logger.debug(f'✓ folder_in exists: {FOLDER_IN}')
            
            # Check and create folder_out if needed
            if not os.path.exists(FOLDER_OUT):
                logger.warning(f'folder_out does not exist: {FOLDER_OUT}')
                logger.debug(f'Creating folder_out: {FOLDER_OUT}')
                try:
                    os.makedirs(FOLDER_OUT, exist_ok=True)
                    logger.debug(f'✓ Created folder_out: {FOLDER_OUT}')
                except Exception as e:
                    raise UserException({
                        'message': f'Cannot create folder_out: {FOLDER_OUT}',
                        'description': str(e)
                    })
            else:
                logger.debug(f'✓ folder_out exists: {FOLDER_OUT}')
            
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

def extract_pacs008_fields(xml_text):
    """Extract sender, receiver, amount, date, currency from pacs.008 XML.

    Returns dict with keys: txt_pay, txt_ben, nsdok, val_code, dval, error.
    """
    result = {
        'txt_pay': None,
        'txt_ben': None,
        'nsdok': None,
        'val_code': None,
        'dval': None,
        'error': None,
    }

    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        # Get full traceback
        tb = traceback.format_exc()
        result['error'] = f'XML parse error: {e}\n\nTraceback:\n{tb}'
        return result

    # Debtor (sender)
    try:
        dbtr = _find_first_by_localname(root, 'Dbtr')
        result['txt_pay'] = _find_child_text_local(dbtr, 'Nm')
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | sender parse error: {e}\nTraceback:\n{tb}'

    # Creditor (receiver)
    try:
        cdtr = _find_first_by_localname(root, 'Cdtr')
        result['txt_ben'] = _find_child_text_local(cdtr, 'Nm')
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | receiver parse error: {e}\nTraceback:\n{tb}'

    # Amount and currency
    try:
        amt_el = _find_first_by_localname(root, 'IntrBkSttlmAmt')
        if amt_el is not None:
            val_text = (amt_el.text or '').strip()
            try:
                # Keep numeric for DB; if fails, store None and keep text in error
                result['nsdok'] = Decimal(val_text)
            except (InvalidOperation, ValueError):
                result['nsdok'] = None
                if val_text:
                    result['error'] = (result['error'] or '') + f' | bad amount: {val_text}'
            result['val_code'] = amt_el.attrib.get('Ccy')
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | amount parse error: {e}\nTraceback:\n{tb}'

    # Value date
    try:
        dval_el = _find_first_by_localname(root, 'IntrBkSttlmDt')
        if dval_el is not None and (dval_el.text or '').strip():
            result['dval'] = (dval_el.text or '').strip()
        else:
            # Fallback to group header creation date/time
            cre_el = _find_first_by_localname(root, 'CreDtTm')
            if cre_el is not None and (cre_el.text or '').strip():
                # Take date part
                result['dval'] = (cre_el.text or '').strip()[:10]
    except Exception as e:
        tb = traceback.format_exc()
        result['error'] = (result['error'] or '') + f' | date parse error: {e}\nTraceback:\n{tb}'

    # If nothing extracted, set an error
    if not any([result['txt_pay'], result['txt_ben'], result['nsdok'], result['val_code'], result['dval']]):
        result['error'] = result['error'] or 'No key fields extracted'

    return result

def create_test_file():
    """Create a test file in the folder_in directory"""
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
            
        # CLEAN DIRECTORY - Remove all existing files
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
            contents_before = []
        except Exception as e:
            logger.error(f'Cannot clean directory: {e}')
            contents_before = []
            
        # Check if directory is writable
        if not os.access(FOLDER_IN, os.W_OK):
            logger.error(f'Input directory is not writable: {FOLDER_IN}')
            # Try to see permissions
            import stat
            try:
                st = os.stat(FOLDER_IN)
                logger.debug(f'Directory permissions: {oct(st.st_mode)}')
                logger.debug(f'Directory owner: {st.st_uid}')
            except:
                pass
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
    
    # Create pacs.008 XML example file (directory is already cleaned)
    logger.debug('Creating pacs.008 XML test file...')

    pacs008_file_path = os.path.join(FOLDER_IN, 'pacs008_example.xml')
    try:
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!--
THE MESSAGE WILL WORK "AS IS" IN THE READINESS PORTAL. IT IS ESSENTIAL THAT USERS REMOVE THE ENVELOPE AND REPLACE IT WITH THEIR OWN TRANSPORT HEADER (FOR EXAMPLE FOR ALLIANCE ACCESS YOU WOULD USE THE XML V2 HEADERS).
=========================================================================================================================================================================================
SWIFT © 2020. All rights reserved.
This publication contains SWIFT or third-party confidential information. Do not disclose this publication outside your organisation without SWIFT's prior written consent.
The use of this document is governed by the legal notices appearing at the end of this document. By using this document, you will be deemed to have accepted those legal notices.
====================================================================================================================================================================
p.8.2.4Agent D NatWest sends a pacs.008 to Agent E RBS
========================================================================================================================
-->
<Envelope xmlns="urn:swift:xsd:envelope" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:swift:xsd:envelope \\\\be-file02\\Group\\Standards\\Messaging\\CBPR+Schemas\\Feb24Schemas_Core\\Translator_envelope_core.xsd">
	<head:AppHdr xmlns:head="urn:iso:std:iso:20022:tech:xsd:head.001.001.02">
		<head:Fr>
			<head:FIId>
				<head:FinInstnId>
					<head:BICFI>NWBKGB2L</head:BICFI>
				</head:FinInstnId>
			</head:FIId>
		</head:Fr>
		<head:To>
			<head:FIId>
				<head:FinInstnId>
					<head:BICFI>RBSSGBKA</head:BICFI>
				</head:FinInstnId>
			</head:FIId>
		</head:To>
		<head:BizMsgIdr>pacs8bizmsgidr02</head:BizMsgIdr>
		<head:MsgDefIdr>pacs.008.001.08</head:MsgDefIdr>
		<head:BizSvc>swift.cbprplus.02</head:BizSvc>
		<head:CreDt>2022-10-20T10:25:00+01:00</head:CreDt>
	</head:AppHdr>
	<pacs:Document xmlns:pacs="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
		<pacs:FIToFICstmrCdtTrf>
			<pacs:GrpHdr>
				<pacs:MsgId>pacs8bizmsgidr02</pacs:MsgId>
				<pacs:CreDtTm>2022-10-20T10:25:00+01:00</pacs:CreDtTm>
				<pacs:NbOfTxs>1</pacs:NbOfTxs>
				<pacs:SttlmInf>
					<pacs:SttlmMtd>INDA</pacs:SttlmMtd>
				</pacs:SttlmInf>
			</pacs:GrpHdr>
			<pacs:CdtTrfTxInf>
				<pacs:PmtId>
					<pacs:InstrId>pacs8bizmsgidr02</pacs:InstrId>
					<pacs:EndToEndId>pacs008EndToEndId-001</pacs:EndToEndId>
					<pacs:UETR>7a562c67-ca16-48ba-b074-65581be6f001</pacs:UETR>
				</pacs:PmtId>
				<pacs:IntrBkSttlmAmt Ccy="USD">98725497</pacs:IntrBkSttlmAmt>
				<pacs:IntrBkSttlmDt>2022-10-20</pacs:IntrBkSttlmDt>
				<pacs:ChrgBr>DEBT</pacs:ChrgBr>
				<pacs:InstgAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>NWBKGB2L</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:InstgAgt>
				<pacs:InstdAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>RBSSGBKA</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:InstdAgt>
				<pacs:Dbtr>
					<pacs:Nm>A Capone</pacs:Nm>
					<pacs:PstlAdr>
						<pacs:StrtNm>180 North Stetson Ave</pacs:StrtNm>
						<pacs:TwnNm>CHICAGO</pacs:TwnNm>
						<pacs:Ctry>US</pacs:Ctry>
					</pacs:PstlAdr>
				</pacs:Dbtr>
				<pacs:DbtrAcct>
					<pacs:Id>
						<pacs:Othr>
							<pacs:Id>ACPN-2569874</pacs:Id>
						</pacs:Othr>
					</pacs:Id>
				</pacs:DbtrAcct>
				<pacs:DbtrAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>AMCDUS44</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:DbtrAgt>
				<pacs:CdtrAgt>
					<pacs:FinInstnId>
						<pacs:BICFI>RBSSGBKA</pacs:BICFI>
					</pacs:FinInstnId>
				</pacs:CdtrAgt>
				<pacs:Cdtr>
					<pacs:Nm>J Smith</pacs:Nm>
					<pacs:PstlAdr>
						<pacs:StrtNm>135 Bishopsgate</pacs:StrtNm>
						<pacs:TwnNm>London</pacs:TwnNm>
						<pacs:Ctry>GB</pacs:Ctry>
					</pacs:PstlAdr>
				</pacs:Cdtr>
				<pacs:CdtrAcct>
					<pacs:Id>
						<pacs:Othr>
							<pacs:Id>65479512</pacs:Id>
						</pacs:Othr>
					</pacs:Id>
				</pacs:CdtrAcct>
			</pacs:CdtTrfTxInf>
		</pacs:FIToFICstmrCdtTrf>
	</pacs:Document>
</Envelope>'''

        with open(pacs008_file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        logger.debug(f'Successfully created pacs.008 XML file: {pacs008_file_path}')
    except Exception as e:
        logger.error(f'Error creating pacs.008 XML file: {e}')

    # Create error test file (invalid XML)
    logger.debug('Creating error test file...')
    error_test_file_path = os.path.join(FOLDER_IN, 'error_test.xml')
    try:
        with open(error_test_file_path, 'w', encoding='utf-8') as f:
            f.write('sample error file')
        logger.debug(f'Successfully created error test file: {error_test_file_path}')
    except Exception as e:
        logger.error(f'Error creating error test file: {e}')

    # List contents AFTER creating file
    try:
        contents_after = os.listdir(FOLDER_IN)
        logger.debug(f'Files AFTER creating test file: {len(contents_after)} files')
        if contents_after:
            for filename in contents_after:
                file_path = os.path.join(FOLDER_IN, filename)
                size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                logger.debug(f'  - {filename} ({size} bytes)')
        else:
            logger.error('  Directory is still empty after creating file!')
    except Exception as e:
        logger.error(f'Cannot list directory after creating file: {e}')

def read_and_import_files():
    """Read all files from folder_in directory and import to swift_input table"""
    global FOLDER_IN
    logger.debug(f'read_and_import_files: Starting with path {FOLDER_IN}')
    
    # Check if directory exists
    if not os.path.exists(FOLDER_IN):
        logger.error(f'Input directory not found: {FOLDER_IN}')
        raise UserException({
            'message': 'Input directory not found',
            'description': f'Path: {FOLDER_IN}'
        })
    
    # Get all files in the directory
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
    
    # Process each file
    imported_count = 0
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
                if len(content) > 50:
                    logger.debug(f'  First 50 chars: {content[:50]}...')
                else:
                    logger.debug(f'  Content: {content}')
                
                # Prepare SQL for insertion
                current_date = datetime.now()
                fields = extract_pacs008_fields(content)
                status_value = 'finished' if not fields.get('error') else 'error'
                
                # Insert into swift_input table with parsed fields (always insert, no duplicate check)
                insert_sql = """
                    INSERT INTO swift_input (
                        file_name, status, content, imported,
                        txt_pay, txt_ben, nsdok, val_code, dval, error
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                c.execute(
                    insert_sql,
                    (
                        filename,
                        status_value,
                        content,
                        current_date,
                        fields.get('txt_pay'),
                        fields.get('txt_ben'),
                        # keep Decimal for numeric DB columns
                        fields.get('nsdok'),
                        fields.get('val_code'),
                        fields.get('dval'),
                        fields.get('error')
                    )
                )
                imported_count += 1
                logger.debug(f'  Successfully imported file: {filename}')
                
                # Move file to folder_out
                dest_file_path = os.path.join(FOLDER_OUT, filename)
                try:
                    shutil.copy2(file_path, dest_file_path)
                    logger.debug(f'  Copied file to: {dest_file_path}')
                except Exception as copy_err:
                    logger.error(f'  Error copying file to folder_out: {copy_err}')
                
                # If there was a parsing error, create .error.txt file
                if fields.get('error'):
                    error_file_path = os.path.join(FOLDER_OUT, f'{filename}.error.txt')
                    try:
                        with open(error_file_path, 'w', encoding='utf-8') as err_f:
                            err_f.write(f'Error processing file: {filename}\n')
                            err_f.write(f'Timestamp: {current_date}\n')
                            err_f.write(f'\nError details:\n{fields.get("error")}\n')
                        logger.debug(f'  Created error file: {error_file_path}')
                    except Exception as err_write:
                        logger.error(f'  Error creating error file: {err_write}')
                
            except UnicodeDecodeError:
                # Try reading as binary if UTF-8 fails
                error_msg = 'UTF-8 decode failed, file imported as hex'
                try:
                    logger.debug(f'  {error_msg} for {filename}')
                    with open(file_path, 'rb') as f:
                        content = f.read().hex()
                    
                    insert_sql = """
                        INSERT INTO swift_input (
                            file_name, status, content, imported, error
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    current_date = datetime.now()

                    c.execute(insert_sql, (filename, 'error', content, current_date, 'binary file imported as hex'))
                    imported_count += 1
                    logger.debug(f'  Imported binary file as hex: {filename}')
                    
                    # Copy file to folder_out
                    dest_file_path = os.path.join(FOLDER_OUT, filename)
                    try:
                        shutil.copy2(file_path, dest_file_path)
                        logger.debug(f'  Copied file to: {dest_file_path}')
                    except Exception as copy_err:
                        logger.error(f'  Error copying file: {copy_err}')
                    
                    # Create error file
                    error_file_path = os.path.join(FOLDER_OUT, f'{filename}.error.txt')
                    try:
                        with open(error_file_path, 'w', encoding='utf-8') as err_f:
                            err_f.write(f'Error processing file: {filename}\n')
                            err_f.write(f'Timestamp: {current_date}\n')
                            err_f.write(f'\nError details:\n{error_msg}\n')
                        logger.debug(f'  Created error file: {error_file_path}')
                    except Exception as err_write:
                        logger.error(f'  Error creating error file: {err_write}')
                        
                except Exception as e:
                    logger.error(f'  Error processing binary file {filename}: {str(e)}')
                    error_count += 1
                    
                    # Still try to copy file and create error file
                    try:
                        dest_file_path = os.path.join(FOLDER_OUT, filename)
                        shutil.copy2(file_path, dest_file_path)
                        
                        error_file_path = os.path.join(FOLDER_OUT, f'{filename}.error.txt')
                        tb = traceback.format_exc()
                        with open(error_file_path, 'w', encoding='utf-8') as err_f:
                            err_f.write(f'Error processing file: {filename}\n')
                            err_f.write(f'Timestamp: {datetime.now()}\n')
                            err_f.write(f'\nError details:\n')
                            err_f.write(f'Binary file processing failed: {str(e)}\n\n')
                            err_f.write(f'Full traceback:\n{tb}')
                    except:
                        pass
                    continue
                    
            except Exception as e:
                logger.error(f'  Error processing file {filename}: {str(e)}')
                error_count += 1
                
                # Copy file to folder_out and create error file with full traceback
                try:
                    dest_file_path = os.path.join(FOLDER_OUT, filename)
                    shutil.copy2(file_path, dest_file_path)
                    logger.debug(f'  Copied file to: {dest_file_path}')
                    
                    error_file_path = os.path.join(FOLDER_OUT, f'{filename}.error.txt')
                    tb = traceback.format_exc()
                    with open(error_file_path, 'w', encoding='utf-8') as err_f:
                        err_f.write(f'Error processing file: {filename}\n')
                        err_f.write(f'Timestamp: {datetime.now()}\n')
                        err_f.write(f'\nError details:\n{str(e)}\n\n')
                        err_f.write(f'Full traceback:\n{tb}')
                    logger.debug(f'  Created error file: {error_file_path}')
                except Exception as copy_err:
                    logger.error(f'  Error copying file or creating error file: {copy_err}')
                continue
        
        # Commit the transaction
        if imported_count > 0:
            c.connection.commit()
            logger.debug(f'Transaction committed: {imported_count} files')
        else:
            logger.warning('No files were imported!')
    
    logger.debug('='*60)
    logger.debug(f'IMPORT SUMMARY:')
    logger.debug(f'  Imported: {imported_count} files')
    logger.debug(f'  Errors: {error_count} files')
    logger.debug(f'  All files copied to: {FOLDER_OUT}')
    if error_count > 0:
        logger.debug(f'  Error details saved in .error.txt files')
    logger.debug('='*60)
    
    return imported_count

def verify_imports():
    """Verify imported records in the database"""
    logger.debug('verify_imports: Starting verification')
    
    sql = """
        SELECT file_name, imported, LENGTH(content) as content_length
        FROM swift_input
        ORDER BY imported DESC
        LIMIT 10
    """
    
    with initDbSession(database='default').cursor() as c:
        try:
            c.execute(sql)
            data = fetchall(c)
            
            logger.debug(f'Found {len(data)} recent imports')
            for row in data:
                logger.debug(f'  File: {row["file_name"]}, Imported: {row["imported"]}, Size: {row["content_length"]} bytes')
                
            return data
        except Exception as e:
            logger.error(f'Error fetching imported records: {e}')
            raise UserException({
                'message': 'Error fetching imported records',
                'description': f'SQL:\n{sql}'
            }).withError(e)

def get_total_records():
    """Get total number of records in swift_input table"""
    logger.debug('get_total_records: Counting total records')

    sql = "SELECT COUNT(*) as total FROM swift_input"

    with initDbSession(database='default').cursor() as c:
        try:
            c.execute(sql)
            result = c.fetchone()

            # Support both tuple-based and dict-based cursor results
            if isinstance(result, dict):
                total = result.get('total', 0)
            elif isinstance(result, (list, tuple)):
                total = result[0] if len(result) > 0 else 0
            else:
                total = 0

            logger.debug(f'Total records in swift_input table: {total}')
            return total
        except Exception as e:
            logger.error(f'Error counting records: {e}')
            return 0

def main():
    """Main execution function"""
    global FOLDER_IN
    
    try:
        # Load settings from database
        load_settings_from_db()
        
        logger.debug('='*80)
        logger.debug('main: Starting SWIFT import process')
        logger.debug(f'Input folder: {FOLDER_IN}')
        logger.debug('='*80)
        
        # Step 1: Create test file
        logger.debug('Step 1: Creating test file...')
        create_test_file()
        
        # Step 2: Read and import files
        logger.debug('Step 2: Reading and importing files...')
        imported_count = read_and_import_files()
        
        # Step 3: Verify imports
        logger.debug('Step 3: Verifying imports...')
        verify_imports()

        # Step 4: Get total records count
        logger.debug('Step 4: Getting total records count...')
        total_records = get_total_records()

        logger.debug('='*80)
        logger.debug('Process completed successfully!')
        logger.debug(f'Total files imported in this run: {imported_count}')
        logger.debug(f'Total records in swift_input table: {total_records}')
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