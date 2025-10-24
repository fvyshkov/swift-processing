#!/usr/bin/env python3
"""
Script to archive and upload swift.objects package to Colvir instance
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path
import subprocess
import json
import requests
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_zip_archive(source_dir, output_zip):
    """
    Create a zip archive from a directory
    
    Args:
        source_dir: Path to the directory to archive
        output_zip: Path to the output zip file
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_path.is_dir():
        raise ValueError(f"Source path is not a directory: {source_dir}")
    
    print(f"Creating archive: {output_zip}")
    print(f"Source directory: {source_dir}")
    
    # Remove old archive if exists
    if os.path.exists(output_zip):
        print(f"Removing old archive: {output_zip}")
        os.remove(output_zip)
    
    # Create zip archive
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through directory
        for root, dirs, files in os.walk(source_path):
            # Filter out .DS_Store but keep .package.info and .configs
            files = [f for f in files if f != '.DS_Store']
            dirs[:] = [d for d in dirs if d != '.DS_Store']
            
            for file in files:
                file_path = Path(root) / file
                # Calculate relative path from source_dir (not parent)
                arcname = file_path.relative_to(source_path)
                print(f"  Adding: {arcname}")
                zipf.write(file_path, arcname)
    
    # Get archive size
    size_bytes = os.path.getsize(output_zip)
    size_kb = size_bytes / 1024
    print(f"✓ Archive created: {output_zip} ({size_kb:.1f} KB)")
    
    return output_zip


def upload_package(zip_file, url, dop_date=None, session_id="COLVIR"):
    """
    Upload package directly to the server
    
    Args:
        zip_file: Path to the zip file
        url: Base URL of the Colvir instance
        dop_date: Optional DOP date
        session_id: Session ID
    """
    print(f"\nUploading package to {url}...")
    
    # Calculate DOP date
    if dop_date:
        dop = dop_date
    else:
        from dateutil.relativedelta import relativedelta
        future_date = datetime.now() + relativedelta(months=11)
        dop = future_date.strftime('%Y-%m-%d')
    
    headers = {
        'Accept': 'application/json,text/plain',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': url,
        'Pragma': 'no-cache',
        'Referer': f'{url}/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'X-ClientVersion': '???',
        'X-ColvirDOP': dop,
        'X-ColvirS': session_id,
        'X-Language': 'EN'
    }
    
    filename = os.path.basename(zip_file)
    
    # Prepare multipart form data
    with open(zip_file, 'rb') as f:
        files = {
            'file': (filename, f, 'application/zip')
        }
        
        data = {
            'object': 'package',
            'method': 'installPackageFile'
        }
        
        api_url = f'{url}/api/aoa/execObjectMethod'
        
        print(f"POST {api_url}")
        response = requests.post(
            api_url,
            headers=headers,
            data=data,
            files=files,
            verify=False
        )
    
    response.raise_for_status()
    print(f"✓ Upload response: {response.status_code}")
    
    return True


def extract_and_run_db_script(source_dir, db_host, db_port, db_name, db_user):
    """
    Extract SQL script from swiftIncome.json and execute it on the database
    
    Args:
        source_dir: Source directory containing ao/swiftIncome.json
        db_host: Database host
        db_port: Database port
        db_name: Database name
        db_user: Database user
    """
    json_path = Path(source_dir) / 'ao' / 'swiftIncome.json'
    
    if not json_path.exists():
        print(f"Warning: {json_path} not found, skipping DB script execution")
        return False
    
    print(f"\nExtracting SQL script from {json_path}...")
    
    try:
        # Read JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Navigate to DB_CREATE_FULL method
        sql_script = data.get('methods', {}).get('DB_CREATE_FULL', {}).get('sql', {}).get('sql', '')
        
        if not sql_script:
            print("Warning: DB_CREATE_FULL SQL script not found in JSON")
            return False
        
        # Replace \n with actual newlines
        sql_script = sql_script.replace('\\n', '\n')
        
        print(f"SQL script extracted ({len(sql_script)} characters)")
        print("Executing SQL script on database...")
        
        # Execute SQL script via psql
        cmd = [
            'psql',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '-c', sql_script
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ SQL execution failed:")
            print(result.stderr)
            return False
        
        print("✓ SQL script executed successfully!")
        if result.stdout:
            # Print only last few lines to avoid spam
            lines = result.stdout.strip().split('\n')
            if len(lines) > 10:
                print("...")
                print('\n'.join(lines[-10:]))
            else:
                print(result.stdout)
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"Error executing DB script: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Archive and upload swift.objects package to Colvir instance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update swift.objects on default instance
  python update_swift_package.py

  # Update on custom instance
  python update_swift_package.py --url http://30.30.1.86:30317

  # Just create archive without uploading
  python update_swift_package.py --no-upload

  # Custom source directory and output file
  python update_swift_package.py --source my.package --output my.package.zip
        """
    )
    
    parser.add_argument(
        '--source',
        default='swift.objects',
        help='Source directory to archive (default: swift.objects)'
    )
    
    parser.add_argument(
        '--output',
        default='swift.objects.zip',
        help='Output zip file name (default: swift.objects.zip)'
    )
    
    parser.add_argument(
        '--url',
        default='http://30.30.1.86:30317',
        help='Base URL of the Colvir instance (default: http://30.30.1.86:30317)'
    )
    
    parser.add_argument(
        '--dop',
        help='Date for X-ColvirDOP header (default: today + 11 months)'
    )
    
    parser.add_argument(
        '--session',
        default='COLVIR',
        help='Session ID for X-ColvirS header (default: COLVIR)'
    )
    
    parser.add_argument(
        '--no-upload',
        action='store_true',
        help='Only create archive without uploading'
    )
    
    # Database options
    parser.add_argument(
        '--skip-db-script',
        action='store_true',
        help='Skip running DB_CREATE_FULL script after upload'
    )
    
    parser.add_argument(
        '--db-host',
        default='30.30.1.34',
        help='Database host (default: 30.30.1.34)'
    )
    
    parser.add_argument(
        '--db-port',
        type=int,
        default=5432,
        help='Database port (default: 5432)'
    )
    
    parser.add_argument(
        '--db-name',
        default='apng_mb',
        help='Database name (default: apng_mb)'
    )
    
    parser.add_argument(
        '--db-user',
        default='apng',
        help='Database user (default: apng)'
    )
    
    args = parser.parse_args()
    
    try:
        # Step 1: Create archive
        zip_file = create_zip_archive(args.source, args.output)
        
        # Step 2: Upload (if not disabled)
        if not args.no_upload:
            upload_package(
                zip_file=zip_file,
                url=args.url,
                dop_date=args.dop,
                session_id=args.session
            )
            print("\n✓ Package updated successfully!")
            
            # Step 3: Run DB script (unless skipped)
            if not args.skip_db_script:
                extract_and_run_db_script(
                    source_dir=args.source,
                    db_host=args.db_host,
                    db_port=args.db_port,
                    db_name=args.db_name,
                    db_user=args.db_user
                )
        else:
            print("\n✓ Archive created (upload skipped)")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

