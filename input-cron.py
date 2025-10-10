import os
import subprocess
import logging
from datetime import datetime
from apng_core.db import initDbSession, fetchall
from apng_core.exceptions import UserException

# Initialize logger
logger = logging.getLogger('cron')

# Log greeting and environment info
logger.debug('===========================================')
logger.debug('Starting SWIFT Income Processing Script')
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
            
        # List current contents BEFORE creating file
        try:
            contents_before = os.listdir(NFS_PATH)
            logger.debug(f'Files BEFORE creating test file: {len(contents_before)} files')
            if contents_before:
                for f in contents_before:
                    logger.debug(f'  - {f}')
            else:
                logger.debug('  Directory is empty')
        except Exception as e:
            logger.error(f'Cannot list directory: {e}')
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
    
    # Create test file ONLY if directory is empty
    if len(contents_before) == 0:
        logger.debug('Directory is empty, creating test files...')
        
        # Create test_file.txt
        test_file_path = os.path.join(NFS_PATH, "test_file.txt")
        try:
            with open(test_file_path, 'w') as f:
                f.write("test")
            logger.debug(f'Successfully created test file: {test_file_path}')
        except Exception as e:
            logger.error(f'Error creating test file: {e}')
            
        # Create sample SWIFT file
        sample_swift_path = os.path.join(NFS_PATH, 'sample_mt103.txt')
        try:
            swift_msg = '{1:F01BANKBEBBAXXX0000000000}'
            swift_msg += '{2:I103BANKDEFFXXXXN}'
            swift_msg += '{3:{108:MT103}}'
            swift_msg += '{4:'
            swift_msg += ':20:1234567890'
            swift_msg += ':23B:CRED'
            swift_msg += ':32A:250110EUR1000,00'
            swift_msg += ':50K:/12345678'
            swift_msg += 'JOHN DOE'
            swift_msg += 'STREET 123'
            swift_msg += ':59:/87654321'
            swift_msg += 'JANE SMITH'
            swift_msg += 'AVENUE 456'
            swift_msg += ':71A:SHA'
            swift_msg += '-}'
            
            with open(sample_swift_path, 'w') as f:
                f.write(swift_msg)
            logger.debug(f'Successfully created sample SWIFT file: {sample_swift_path}')
        except Exception as e:
            logger.error(f'Error creating sample SWIFT file: {e}')
            
        # List contents AFTER creating files
        try:
            contents_after = os.listdir(NFS_PATH)
            logger.debug(f'Files AFTER creating test files: {len(contents_after)} files')
            if contents_after:
                for filename in contents_after:
                    file_path = os.path.join(NFS_PATH, filename)
                    size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                    logger.debug(f'  - {filename} ({size} bytes)')
            else:
                logger.error('  Directory is still empty after creating files!')
        except Exception as e:
            logger.error(f'Cannot list directory after creating files: {e}')
    else:
        logger.debug(f'Directory already contains {len(contents_before)} files, skipping test file creation')

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
                
                # Check if file already exists in database
                check_sql = """
                    SELECT COUNT(*) as cnt
                    FROM swift_input
                    WHERE file_name = %s
                """
                
                c.execute(check_sql, (filename,))
                result = c.fetchone()
                
                if result and result['cnt'] > 0:
                    logger.debug(f'  File {filename} already exists in database, skipping...')
                    skipped_count += 1
                    continue
                
                # Insert into swift_input table
                insert_sql = """
                    INSERT INTO swift_input (file_name, content, imported)
                    VALUES (%s, %s, %s)
                """
                
                c.execute(insert_sql, (filename, content, current_date))
                imported_count += 1
                logger.debug(f'  Successfully imported file: {filename}')
                
            except UnicodeDecodeError:
                # Try reading as binary if UTF-8 fails
                try:
                    logger.debug(f'  UTF-8 decode failed, trying binary for {filename}')
                    with open(file_path, 'rb') as f:
                        content = f.read().hex()
                    
                    insert_sql = """
                        INSERT INTO swift_input (file_name, content, imported)
                        VALUES (%s, %s, %s)
                    """
                    current_date = datetime.now()
                    
                    c.execute(insert_sql, (filename, content, current_date))
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
        
        logger.debug('='*80)
        logger.debug('Process completed successfully!')
        logger.debug(f'Total files imported: {imported_count}')
        
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