#!/usr/bin/env python3
"""
Script to upload packages to Colvir instance
"""

import argparse
import os
import sys
import requests
from datetime import datetime
import json
import time


class PackageUploader:
    def __init__(self, base_url, dop_date=None, session_id="COLVIR"):
        """
        Initialize package uploader
        
        Args:
            base_url: Base URL of the instance (e.g., http://30.30.1.86:30317)
            dop_date: Date for X-ColvirDOP header (default: today + 11 months)
            session_id: Session ID for X-ColvirS header (default: COLVIR)
        """
        self.base_url = base_url.rstrip('/')
        self.session_id = session_id
        
        # Calculate DOP date (today + 11 months if not provided)
        if dop_date:
            self.dop_date = dop_date
        else:
            # Default: today + 11 months
            from dateutil.relativedelta import relativedelta
            future_date = datetime.now() + relativedelta(months=11)
            self.dop_date = future_date.strftime('%Y-%m-%d')
        
        self.headers = {
            'Accept': 'application/json,text/plain',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': self.base_url,
            'Pragma': 'no-cache',
            'Referer': f'{self.base_url}/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'X-ClientVersion': '???',
            'X-ColvirDOP': self.dop_date,
            'X-ColvirS': self.session_id,
            'X-Language': 'EN',
            'X-Requested-With': 'XMLHttpRequest'
        }
    
    def upload_package(self, package_path):
        """
        Upload package file to the instance
        
        Args:
            package_path: Path to the package zip file
            
        Returns:
            dict: Response from the server with package ID
        """
        if not os.path.exists(package_path):
            raise FileNotFoundError(f"Package file not found: {package_path}")
        
        filename = os.path.basename(package_path)
        print(f"Uploading package: {filename}")
        
        # Prepare multipart form data
        with open(package_path, 'rb') as f:
            files = {
                'file': (filename, f, 'application/zip')
            }
            
            data = {
                'object': 'package',
                'method': 'installPackageFile'
            }
            
            # Use headers without Content-Type for multipart request
            upload_headers = self.headers.copy()
            upload_headers.pop('X-Requested-With', None)  # Not needed for file upload
            
            url = f'{self.base_url}/api/aoa/execObjectMethod'
            
            print(f"POST {url}")
            response = requests.post(
                url,
                headers=upload_headers,
                data=data,
                files=files,
                verify=False  # --insecure
            )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"Upload response: {json.dumps(result, indent=2)}")
        return result
    
    def get_package_list(self, package_id=None):
        """
        Get package list or specific package info
        
        Args:
            package_id: Optional package ID to get info for
            
        Returns:
            dict: Package list or info
        """
        url = f'{self.base_url}/api/aoa/execObjectMethod'
        
        payload = {
            'object': 'package',
            'method': 'getList',
            'params': {}
        }
        
        if package_id:
            payload['params']['id'] = package_id
        
        self.headers['Content-Type'] = 'application/json'
        
        print(f"Getting package info...")
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            verify=False
        )
        
        response.raise_for_status()
        result = response.json()
        
        print(f"Package info: {json.dumps(result, indent=2)}")
        return result
    
    def upload_and_verify(self, package_path, wait_time=2):
        """
        Upload package and verify it was uploaded successfully
        
        Args:
            package_path: Path to the package zip file
            wait_time: Time to wait between upload and verification (seconds)
            
        Returns:
            dict: Final package info
        """
        # Step 1: Upload package
        upload_result = self.upload_package(package_path)
        
        # Extract package ID from response
        package_id = None
        if isinstance(upload_result, dict):
            # Try to find package ID in different possible locations
            package_id = (
                upload_result.get('id') or 
                upload_result.get('packageId') or 
                upload_result.get('data', {}).get('id')
            )
        
        if not package_id:
            print("Warning: Could not extract package ID from upload response")
            print("Waiting and checking package list...")
        
        # Step 2: Wait a bit for the server to process
        time.sleep(wait_time)
        
        # Step 3: Get package info
        if package_id:
            package_info = self.get_package_list(package_id)
        else:
            package_info = self.get_package_list()
        
        return package_info


def main():
    parser = argparse.ArgumentParser(
        description='Upload package to Colvir instance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload to default instance
  python upload_package.py mb.local.zip

  # Upload to custom instance
  python upload_package.py mb.local.zip --url http://30.30.1.86:30317

  # Specify custom DOP date and session
  python upload_package.py mb.local.zip --dop 2025-12-31 --session ADMIN
        """
    )
    
    parser.add_argument(
        'package',
        help='Path to the package zip file'
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
        '--no-verify',
        action='store_true',
        help='Do not verify package after upload'
    )
    
    args = parser.parse_args()
    
    try:
        # Disable SSL warnings for --insecure requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        uploader = PackageUploader(
            base_url=args.url,
            dop_date=args.dop,
            session_id=args.session
        )
        
        if args.no_verify:
            uploader.upload_package(args.package)
        else:
            uploader.upload_and_verify(args.package)
        
        print("\n✓ Package uploaded successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

