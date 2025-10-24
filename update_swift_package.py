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
    Upload package using upload_package.py script
    
    Args:
        zip_file: Path to the zip file
        url: Base URL of the Colvir instance
        dop_date: Optional DOP date
        session_id: Session ID
    """
    print(f"\nUploading package to {url}...")
    
    # Build command
    cmd = [
        sys.executable,  # Use the same Python interpreter
        'upload_package.py',
        zip_file,
        '--url', url
    ]
    
    if dop_date:
        cmd.extend(['--dop', dop_date])
    
    if session_id != 'COLVIR':
        cmd.extend(['--session', session_id])
    
    # Run upload script
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed with exit code {result.returncode}")
    
    return True


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

