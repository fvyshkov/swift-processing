#!/usr/bin/env python3
"""
Sync swift_job_script.py back to swift.objects/ao/swiftIncome.json
"""
import json

def main():
    # Read the Python script
    with open('swift_job_script.py', 'r', encoding='utf-8') as f:
        script_content = f.read()

    # Read the JSON file
    with open('swift.objects/ao/swiftIncome.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update the script content
    data['methods']['job']['script']['py'] = script_content

    # Write back to JSON
    with open('swift.objects/ao/swiftIncome.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("✓ Synced swift_job_script.py → swift.objects/ao/swiftIncome.json")

if __name__ == '__main__':
    main()
