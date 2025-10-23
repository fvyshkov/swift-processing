#!/usr/bin/env python3
"""
Test script for Claude API address parsing
Tests the HTTP request functionality without database dependencies
"""

import json
import requests

# Claude API configuration
CLAUDE_API_KEY = "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"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"


def test_parse_address(address_string):
    """Test address parsing with Claude API"""
    print(f"\n{'='*60}")
    print(f"Testing address: {address_string}")
    print('='*60)
    
    prompt = f"""Parse the following address into structured fields. Return ONLY a JSON object with these exact keys: postal_code, country, region, city, street, building.

Address: {address_string}

Rules:
- If a field is not present in the address, use null
- Extract postal/zip code if present
- Identify country (full name or code)
- Extract region/oblast/state if present
- Extract city/town name
- Extract street name
- Extract building/house number

Return ONLY the JSON object, no explanations."""

    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 500,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        response_data = response.json()
        response_text = response_data['content'][0]['text'].strip()
        
        print("\nClaude Response:")
        print(response_text)
        
        # Parse JSON
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            json_lines = [l for l in lines if l and not l.startswith('```') and not l.startswith('json')]
            response_text = '\n'.join(json_lines)
        
        parsed = json.loads(response_text)
        
        print("\nParsed Result:")
        for key, value in parsed.items():
            print(f"  {key}: {value}")
        
        return parsed
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ HTTP request error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parse error: {e}")
        print(f"Response text was: {response_text}")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("="*60)
    print("Claude API Address Parsing Test")
    print("="*60)
    
    # Test cases
    test_addresses = [
        "г. Москва, ул. Тверская, д. 10, кв. 5, 125009",
        "Россия, 190000, Санкт-Петербург, Невский проспект, дом 28",
        "Узбекистан, Ташкент, Мирабадский район, ул. Афросиаб, 14",
        "100047, г. Ташкент, Яккасарайский район, ул. Фараби, 12А",
        "123 Main Street, Apt 5B, New York, NY 10001, USA"
    ]
    
    success_count = 0
    for address in test_addresses:
        result = test_parse_address(address)
        if result:
            success_count += 1
        print()
    
    print("="*60)
    print(f"Results: {success_count}/{len(test_addresses)} successful")
    print("="*60)

