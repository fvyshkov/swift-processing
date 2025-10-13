#!/usr/bin/env python3
"""Test balance parsing with the fixed code"""
import xml.etree.ElementTree as ET
from decimal import Decimal
import psycopg2
import os

def _find_first_by_localname(root, localname):
    """Return first element in tree by localname, ignoring namespaces."""
    for el in root.iter():
        tag = el.tag
        if isinstance(tag, str) and (tag.endswith('}' + localname) or tag == localname):
            return el
    return None

def _find_all_by_localname(parent, localname):
    """Find all descendant elements by local name (ignoring namespace)."""
    results = []
    for elem in parent.iter():
        if elem.tag.endswith('}' + localname) or elem.tag == localname:
            results.append(elem)
    return results

# Parse XML
tree = ET.parse('test_data/folder_in/camt053_example.xml')
root = tree.getroot()

# Find Stmt using iter (searches all descendants)
stmt = None
for elem in root.iter():
    if elem.tag.endswith('}Stmt'):
        stmt = elem
        break
if stmt is None:
    print("ERROR: No Stmt found")
    exit(1)

bal_elements = _find_all_by_localname(stmt, 'Bal')
print(f"Found {len(bal_elements)} balance elements\n")

balances_to_insert = []

for i, bal_el in enumerate(bal_elements, 1):
    print(f"=== Balance {i} ===")

    # Extract balance type
    tp_cd_el = _find_first_by_localname(bal_el, 'Cd')
    tp_cd = (tp_cd_el.text or '').strip() if tp_cd_el is not None else None
    print(f"  Type code: {tp_cd}")

    # Extract amount
    amt_el = _find_first_by_localname(bal_el, 'Amt')
    if amt_el is None:
        print("  ERROR: No Amt element")
        continue

    amt_text = (amt_el.text or '').strip()
    amt_ccy = amt_el.attrib.get('Ccy')
    try:
        amt = Decimal(amt_text)
    except:
        amt = None
    print(f"  Amount: {amt} {amt_ccy}")

    # Extract credit/debit indicator
    cdt_dbt_ind_el = _find_first_by_localname(bal_el, 'CdtDbtInd')
    cdt_dbt_ind = (cdt_dbt_ind_el.text or '').strip() if cdt_dbt_ind_el is not None else None
    print(f"  Cdt/Dbt: {cdt_dbt_ind}")

    # Extract date (NEW FIXED VERSION - Dt/Dt structure)
    dt_container = _find_first_by_localname(bal_el, 'Dt')
    dt_text = None
    if dt_container is not None:
        # Look for a child Dt element (skip the container itself)
        for child_dt in dt_container.iter():
            if child_dt is not dt_container and (child_dt.tag.endswith('}Dt') or child_dt.tag == 'Dt'):
                dt_text = (child_dt.text or '').strip()
                break
    print(f"  Date: {dt_text}")

    # Check if we can insert
    if tp_cd and amt is not None and cdt_dbt_ind and dt_text:
        print(f"  ✓ Ready to insert")
        balances_to_insert.append((tp_cd, amt, amt_ccy, cdt_dbt_ind, dt_text))
    else:
        print(f"  ✗ Missing data: tp_cd={tp_cd}, amt={amt}, cdt_dbt_ind={cdt_dbt_ind}, dt={dt_text}")
    print()

print(f"\n=== Summary ===")
print(f"Total balances found: {len(bal_elements)}")
print(f"Balances ready to insert: {len(balances_to_insert)}")

if len(balances_to_insert) == 4:
    print("\n✓ SUCCESS: All 4 balances parsed correctly!")
else:
    print(f"\n✗ FAIL: Expected 4 balances, got {len(balances_to_insert)}")
