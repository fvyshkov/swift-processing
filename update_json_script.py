#!/usr/bin/env python3
"""
Script to update the job.script.py field in swiftIncome.json
"""
import json
import os

def main():
    json_path = 'swift.objects/ao/swiftIncome.json'
    new_script_path = 'new_job_script.py'

    # Read new script
    print(f'Reading new script from {new_script_path}...')
    with open(new_script_path, 'r', encoding='utf-8') as f:
        new_script_content = f.read()

    print(f'New script size: {len(new_script_content)} characters')

    # Read JSON
    print(f'Reading JSON from {json_path}...')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update the script
    if 'methods' in data and 'job' in data['methods'] and 'script' in data['methods']['job']:
        old_script = data['methods']['job']['script'].get('py', '')
        print(f'Old script size: {len(old_script)} characters')

        data['methods']['job']['script']['py'] = new_script_content
        print('Updated script in JSON data')
    else:
        print('ERROR: Cannot find methods.job.script.py in JSON structure')
        return 1

    # Write updated JSON
    print(f'Writing updated JSON to {json_path}...')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'✓ Successfully updated {json_path}')
    print(f'✓ New script size: {len(new_script_content)} characters')

    return 0

if __name__ == '__main__':
    exit(main())
