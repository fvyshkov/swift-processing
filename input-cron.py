import os
import subprocess
import logging
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

# Check for SWIFT_PATH environment variable
SWIFT_PATH_ENV = os.environ.get('SWIFT_PATH', 'NOT_SET')
logger.debug(f'Environment variable SWIFT_PATH: {SWIFT_PATH_ENV}')

# NFS configuration
NFS_SERVER = "30.30.1.84"
NFS_REMOTE_PATH = "/var/local/nfs/apng-apng-swift-pvc-d6e31bb3-44fa-4445-b22a-8faa47da7d8a"
NFS_LOCAL_MOUNT = "/mnt/swift_nfs"

# Global variable for NFS path
NFS_PATH = None

def ensure_nfs_mounted():
    """Ensure NFS is mounted"""
    global NFS_PATH
    
    # If SWIFT_PATH is set in environment, use it
    if SWIFT_PATH_ENV != 'NOT_SET':
        logger.debug(f'SWIFT_PATH environment variable is set to: {SWIFT_PATH_ENV}')
        if os.path.exists(SWIFT_PATH_ENV):
            NFS_PATH = SWIFT_PATH_ENV
            logger.debug(f'Path exists! Using SWIFT_PATH from environment: {NFS_PATH}')
            # List contents to verify
            try:
                contents = os.listdir(NFS_PATH)
                logger.debug(f'Directory contains {len(contents)} items')
                if contents:
                    logger.debug(f'First few items: {contents[:3]}')
            except Exception as e:
                logger.error(f'Cannot list directory contents: {e}')
            return NFS_PATH
        else:
            logger.warning(f'SWIFT_PATH {SWIFT_PATH_ENV} does not exist!')
    
    logger.debug('SWIFT_PATH not set or does not exist, will try to find/mount NFS')
    
    try:
        logger.debug('Checking NFS mount status...')
        
        # Check if already mounted
        result = subprocess.run(['mount'], capture_output=True, text=True)
        if NFS_SERVER in result.stdout and NFS_LOCAL_MOUNT in result.stdout:
            logger.debug(f'NFS already mounted at {NFS_LOCAL_MOUNT}')
            NFS_PATH = NFS_LOCAL_MOUNT
            return NFS_LOCAL_MOUNT
        
        # Create mount point if doesn't exist
        if not os.path.exists(NFS_LOCAL_MOUNT):
            logger.debug(f'Creating mount point: {NFS_LOCAL_MOUNT}')
            os.makedirs(NFS_LOCAL_MOUNT, exist_ok=True)
        
        # Try to mount NFS
        mount_cmd = [
            'mount', '-t', 'nfs',
            f'{NFS_SERVER}:{NFS_REMOTE_PATH}',
            NFS_LOCAL_MOUNT
        ]
        
        logger.debug(f'Mounting NFS: {NFS_SERVER}:{NFS_REMOTE_PATH} -> {NFS_LOCAL_MOUNT}')
        result = subprocess.run(mount_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.debug(f'Mount failed: {result.stderr}')
            logger.debug('Trying with nfs4...')
            mount_cmd[2] = 'nfs4'
            result = subprocess.run(mount_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f'Failed to mount NFS: {result.stderr}')
        
        logger.debug('NFS mounted successfully')
        NFS_PATH = NFS_LOCAL_MOUNT
        return NFS_LOCAL_MOUNT
        
    except Exception as e:
        logger.warning(f'Could not mount NFS: {e}')
        logger.debug('Trying alternative paths...')
        
        # Try alternative paths that might already be mounted
        alternative_paths = [
            "/var/local/nfs/apng-apng-swift-pvc-d6e31bb3-44fa-4445-b22a-8faa47da7d8a",
            "/data/swift",
            "/tmp/swift_test"
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                logger.debug(f'Found existing path: {path}')
                NFS_PATH = path
                return path
        
        # If nothing works, create test directory
        test_path = "/tmp/swift_test"
        os.makedirs(test_path, exist_ok=True)
        logger.debug(f'Using test path: {test_path}')
        NFS_PATH = test_path
        return test_path

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
        result['error'] = f'XML parse error: {e}'
        return result

    # Debtor (sender)
    try:
        dbtr = _find_first_by_localname(root, 'Dbtr')
        result['txt_pay'] = _find_child_text_local(dbtr, 'Nm')
    except Exception as e:
        result['error'] = (result['error'] or '') + f' | sender parse: {e}'

    # Creditor (receiver)
    try:
        cdtr = _find_first_by_localname(root, 'Cdtr')
        result['txt_ben'] = _find_child_text_local(cdtr, 'Nm')
    except Exception as e:
        result['error'] = (result['error'] or '') + f' | receiver parse: {e}'

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
        result['error'] = (result['error'] or '') + f' | amount parse: {e}'

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
        result['error'] = (result['error'] or '') + f' | date parse: {e}'

    # If nothing extracted, set an error
    if not any([result['txt_pay'], result['txt_ben'], result['nsdok'], result['val_code'], result['dval']]):
        result['error'] = result['error'] or 'No key fields extracted'

    return result

def create_test_file():
    """Create a test file in the NFS directory"""
    global NFS_PATH
    logger.debug(f'create_test_file: Starting with path {NFS_PATH}')
    
    # Check if directory exists
    try:
        if not os.path.exists(NFS_PATH):
            logger.debug(f'Directory {NFS_PATH} does not exist, creating it...')
            os.makedirs(NFS_PATH, exist_ok=True)
            logger.debug(f'Directory created: {NFS_PATH}')
        else:
            logger.debug(f'Directory exists: {NFS_PATH}')
            
        # CLEAN DIRECTORY - Remove all existing files
        try:
            contents_before = os.listdir(NFS_PATH)
            if contents_before:
                logger.debug(f'Cleaning directory: found {len(contents_before)} files to remove')
                for filename in contents_before:
                    file_path = os.path.join(NFS_PATH, filename)
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
        if not os.access(NFS_PATH, os.W_OK):
            logger.error(f'NFS directory is not writable: {NFS_PATH}')
            # Try to see permissions
            import stat
            try:
                st = os.stat(NFS_PATH)
                logger.debug(f'Directory permissions: {oct(st.st_mode)}')
                logger.debug(f'Directory owner: {st.st_uid}')
            except:
                pass
            raise UserException({
                'message': 'NFS directory is not writable',
                'description': f'Path: {NFS_PATH}'
            })
        else:
            logger.debug(f'Directory is writable')
    except Exception as e:
        logger.error(f'Error checking/creating NFS directory: {e}')
        raise UserException({
            'message': 'Error checking/creating NFS directory',
            'description': f'Path: {NFS_PATH}'
        }).withError(e)
    
    # Create pacs.008 XML example file (directory is already cleaned)
    logger.debug('Creating pacs.008 XML test file...')

    pacs008_file_path = os.path.join(NFS_PATH, 'pacs008_example.xml')
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

    # List contents AFTER creating file
    try:
        contents_after = os.listdir(NFS_PATH)
        logger.debug(f'Files AFTER creating test file: {len(contents_after)} files')
        if contents_after:
            for filename in contents_after:
                file_path = os.path.join(NFS_PATH, filename)
                size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                logger.debug(f'  - {filename} ({size} bytes)')
        else:
            logger.error('  Directory is still empty after creating file!')
    except Exception as e:
        logger.error(f'Cannot list directory after creating file: {e}')

def read_and_import_files():
    """Read all files from NFS directory and import to swift_input table"""
    global NFS_PATH
    logger.debug(f'read_and_import_files: Starting with path {NFS_PATH}')
    
    # Check if directory exists
    if not os.path.exists(NFS_PATH):
        logger.error(f'NFS directory not found: {NFS_PATH}')
        raise UserException({
            'message': 'NFS directory not found',
            'description': f'Path: {NFS_PATH}'
        })
    
    # Get all files in the directory
    try:
        files = [f for f in os.listdir(NFS_PATH) if os.path.isfile(os.path.join(NFS_PATH, f))]
        logger.debug(f'Found {len(files)} files in {NFS_PATH}')
        if files:
            logger.debug(f'Files to process:')
            for filename in files:
                file_path = os.path.join(NFS_PATH, filename)
                size = os.path.getsize(file_path)
                logger.debug(f'  - {filename} ({size} bytes)')
        else:
            logger.warning('No files found in directory!')
            return 0
    except Exception as e:
        logger.error(f'Error reading NFS directory: {e}')
        raise UserException({
            'message': 'Error reading NFS directory',
            'description': f'Path: {NFS_PATH}'
        }).withError(e)
    
    # Process each file
    imported_count = 0
    skipped_count = 0
    error_count = 0
    
    with initDbSession(database='default').cursor() as c:
        for filename in files:
            file_path = os.path.join(NFS_PATH, filename)
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
                
                # Check if file already exists in database
                check_sql = """
                    SELECT COUNT(*) as cnt
                    FROM swift_input
                    WHERE file_name = %s
                """
                
                c.execute(check_sql, (filename,))
                result = c.fetchone()

                # Support both tuple-based and dict-based cursor results
                try:
                    if isinstance(result, dict):
                        existing_count = result.get('cnt', 0)
                    elif isinstance(result, (list, tuple)):
                        existing_count = result[0] if len(result) > 0 else 0
                    else:
                        existing_count = 0
                except Exception:
                    existing_count = 0

                if existing_count > 0:
                    logger.debug(f'  File {filename} already exists in database, skipping...')
                    skipped_count += 1
                    continue
                
                # Insert into swift_input table with parsed fields
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
                
            except UnicodeDecodeError:
                # Try reading as binary if UTF-8 fails
                try:
                    logger.debug(f'  UTF-8 decode failed, trying binary for {filename}')
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
                except Exception as e:
                    logger.error(f'  Error processing binary file {filename}: {str(e)}')
                    error_count += 1
                    continue
            except Exception as e:
                logger.error(f'  Error processing file {filename}: {str(e)}')
                error_count += 1
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
    logger.debug(f'  Skipped (already in DB): {skipped_count} files')
    logger.debug(f'  Errors: {error_count} files')
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
    global NFS_PATH
    
    try:
        # Initialize NFS path
        ensure_nfs_mounted()
        
        logger.debug('='*80)
        logger.debug('main: Starting NFS Swift import process')
        logger.debug(f'NFS Server: {NFS_SERVER}')
        logger.debug(f'NFS Remote Path: {NFS_REMOTE_PATH}')
        logger.debug(f'Using Local Path: {NFS_PATH}')
        logger.debug('='*80)
        
        # Check current working directory and user
        logger.debug(f'Current directory: {os.getcwd()}')
        logger.debug(f'Current user: {os.getuid() if hasattr(os, "getuid") else "unknown"}')
        
        # Log all environment variables with SWIFT in name
        logger.debug('Environment variables containing SWIFT:')
        for key, value in os.environ.items():
            if 'SWIFT' in key.upper():
                logger.debug(f'  {key}={value}')
        
        # Check mount status
        logger.debug('Checking mount status...')
        result = subprocess.run(['mount'], capture_output=True, text=True)
        nfs_mounts = [line for line in result.stdout.split('\n') if 'nfs' in line.lower()]
        if nfs_mounts:
            logger.debug('NFS mounts found:')
            for mount in nfs_mounts[:3]:
                logger.debug(f'  {mount[:100]}...')
        else:
            logger.debug('No NFS mounts found')
        
        # Check if we're in Kubernetes
        if os.path.exists('/var/run/secrets/kubernetes.io'):
            logger.debug('Running in Kubernetes environment')
            logger.debug('Checking for PVC mounts...')
            found_swift_path = False
            for root, dirs, files in os.walk('/var'):
                if 'swift' in root.lower() or 'd6e31bb3' in root:
                    logger.debug(f'  Found potential Swift path: {root}')
                    if os.access(root, os.W_OK):
                        logger.debug(f'    -> Writable! Using this path')
                        NFS_PATH = root
                        found_swift_path = True
                        break
            if not found_swift_path:
                logger.debug('No Swift path found in /var, keeping current NFS_PATH')
        
        # List parent directory to debug
        parent_dir = os.path.dirname(NFS_PATH)
        if os.path.exists(parent_dir):
            logger.debug(f'Contents of {parent_dir}:')
            try:
                items = os.listdir(parent_dir)
                for item in items[:5]:
                    logger.debug(f'  - {item}')
                if len(items) > 5:
                    logger.debug(f'  ... and {len(items)-5} more items')
            except Exception as e:
                logger.debug(f'  Cannot list directory: {e}')
        
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