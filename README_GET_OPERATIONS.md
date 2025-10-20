# Get Available Operations by Document ID

## Overview

Python module to retrieve available operations for a SWIFT document based on its current state.

## Features

- ✓ Get document information by ID
- ✓ Retrieve current state details
- ✓ List available operations for current state
- ✓ Replace URL placeholders automatically
- ✓ Parse availability conditions
- ✓ Support for verbose and JSON output

## Installation

No installation needed. Just import the module:

```python
from get_operations import get_document_operations, get_operations_by_document_id
```

## Usage

### 1. As Command Line Tool

**Basic usage:**
```bash
python3 get_operations.py <document_uuid>
```

**Verbose mode:**
```bash
python3 get_operations.py <document_uuid> -v
```

**JSON output:**
```bash
python3 get_operations.py <document_uuid> -j
```

### 2. As Python Module

#### Simple: Get just the operations list

```python
from get_operations import get_operations_by_document_id

document_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
operations = get_operations_by_document_id(document_id)

for op in operations:
    print(f"{op['icon']} {op['name_ru']}")
```

#### Complete: Get full document info with operations

```python
from get_operations import get_document_operations

document_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
result = get_document_operations(document_id, verbose=True)

if result['success']:
    doc = result['document']
    state = result['state']
    operations = result['operations']
    
    print(f"Document: {doc['file_name']}")
    print(f"Type: {doc['msg_type']}")
    print(f"State: {state['name_ru']}")
    print(f"Operations: {len(operations)}")
    
    for op in operations:
        print(f"  - {op['name_ru']} → {op['target_state']}")
else:
    print(f"Error: {result['error']}")
```

#### Low-level: Use individual functions

```python
from apng_core.db import initDbSession
from get_operations import get_document_info, get_available_operations, get_state_info

with initDbSession(database='default').cursor() as c:
    # Get document
    doc = get_document_info(c, document_id)
    
    # Get state
    state = get_state_info(c, doc['msg_type'], doc['state'])
    
    # Get operations
    operations = get_available_operations(c, document_id)
```

## Return Format

### get_document_operations() Returns:

```python
{
    'success': True,
    'document': {
        'id': 'uuid',
        'file_name': 'filename.xml',
        'msg_type': 'pacs.008',
        'state': 'LOADED',
        'imported': datetime,
        'amount': Decimal('1000.00'),
        'currency_code': 'USD',
        'msg_id': 'MSG123',
        'sender_name': 'Sender Name',
        'receiver_name': 'Receiver Name'
    },
    'state': {
        'id': 'uuid',
        'code': 'LOADED',
        'name_en': 'Loaded',
        'name_ru': 'Загружен',
        'name_combined': 'Loaded (Загружен)',
        'color_code': '#FF8C00',
        'allow_edit': True,
        'allow_delete': True
    },
    'operations': [
        {
            'id': 'uuid',
            'code': 'MARK_AS_PROCESSED',
            'name_en': 'Mark as Processed',
            'name_ru': 'Отметить как обработанный',
            'name_combined': 'Mark as Processed (Отметить как обработанный)',
            'icon': 'check',
            'resource_url': '/aoa/ProcessAction?action=markProcessed&docId=uuid&docType=pacs.008',
            'target_state': 'PROCESSED',
            'current_state': 'LOADED',
            'document_type': 'pacs.008'
        },
        {
            'id': 'uuid',
            'code': 'CREATE_PAYMENT',
            'name_en': 'Create Payment',
            'name_ru': 'Создать платеж',
            'name_combined': 'Create Payment (Создать платеж)',
            'icon': 'payment',
            'resource_url': '/aoa/ProcessAction?action=createPayment&docId=uuid&docType=pacs.008',
            'target_state': 'PAYMENT_CREATED',
            'current_state': 'LOADED',
            'document_type': 'pacs.008'
        }
    ]
}
```

### get_operations_by_document_id() Returns:

```python
[
    {
        'id': 'uuid',
        'code': 'MARK_AS_PROCESSED',
        'name_ru': 'Отметить как обработанный',
        'icon': 'check',
        'resource_url': '/aoa/ProcessAction?...',
        'target_state': 'PROCESSED',
        ...
    },
    ...
]
```

## Command Line Examples

### Example 1: Basic Usage

```bash
$ python3 get_operations.py a1b2c3d4-e5f6-7890-abcd-ef1234567890

Available operations for document a1b2c3d4-e5f6-7890-abcd-ef1234567890:
  - [check] Отметить как обработанный (MARK_AS_PROCESSED)
  - [payment] Создать платеж (CREATE_PAYMENT)

Total: 2 operation(s)
```

### Example 2: Verbose Output

```bash
$ python3 get_operations.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 -v

======================================================================
Document Information
======================================================================
ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
File: pacs008_example.xml
Type: pacs.008
State: LOADED
Message ID: MSG20231020001
Amount: 1000.00 USD
Sender: ABC Bank
Receiver: XYZ Corporation
Imported: 2025-10-20 10:30:00

Current State Information
----------------------------------------------------------------------
State: Loaded (Загружен)
Color: #FF8C00
Allow Edit: True
Allow Delete: True

Available Operations
----------------------------------------------------------------------

1. Mark as Processed (Отметить как обработанный)
   Code: MARK_AS_PROCESSED
   Icon: check
   Target State: PROCESSED
   URL: /aoa/ProcessAction?action=markProcessed&docId=a1b2...&docType=pacs.008

2. Create Payment (Создать платеж)
   Code: CREATE_PAYMENT
   Icon: payment
   Target State: PAYMENT_CREATED
   URL: /aoa/ProcessAction?action=createPayment&docId=a1b2...&docType=pacs.008

======================================================================
```

### Example 3: JSON Output

```bash
$ python3 get_operations.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 -j
```

```json
{
  "success": true,
  "document": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "file_name": "pacs008_example.xml",
    "msg_type": "pacs.008",
    "state": "LOADED",
    "imported": "2025-10-20 10:30:00",
    "amount": "1000.00",
    "currency_code": "USD",
    "msg_id": "MSG20231020001",
    "sender_name": "ABC Bank",
    "receiver_name": "XYZ Corporation"
  },
  "state": {
    "id": "state-uuid",
    "code": "LOADED",
    "name_en": "Loaded",
    "name_ru": "Загружен",
    "name_combined": "Loaded (Загружен)",
    "color_code": "#FF8C00",
    "allow_edit": true,
    "allow_delete": true
  },
  "operations": [
    {
      "id": "op-uuid-1",
      "code": "MARK_AS_PROCESSED",
      "name_en": "Mark as Processed",
      "name_ru": "Отметить как обработанный",
      "name_combined": "Mark as Processed (Отметить как обработанный)",
      "icon": "check",
      "resource_url": "/aoa/ProcessAction?action=markProcessed&docId=a1b2...&docType=pacs.008",
      "target_state": "PROCESSED",
      "current_state": "LOADED",
      "document_type": "pacs.008"
    },
    {
      "id": "op-uuid-2",
      "code": "CREATE_PAYMENT",
      "name_en": "Create Payment",
      "name_ru": "Создать платеж",
      "name_combined": "Create Payment (Создать платеж)",
      "icon": "payment",
      "resource_url": "/aoa/ProcessAction?action=createPayment&docId=a1b2...&docType=pacs.008",
      "target_state": "PAYMENT_CREATED",
      "current_state": "LOADED",
      "document_type": "pacs.008"
    }
  ]
}
```

## Integration Examples

### In Web Application

```python
from flask import Flask, jsonify
from get_operations import get_document_operations

app = Flask(__name__)

@app.route('/api/documents/<document_id>/operations')
def get_doc_operations(document_id):
    result = get_document_operations(document_id)
    return jsonify(result)
```

### In BPMN Process

```python
from get_operations import get_operations_by_document_id

# In BPMN script task
document_id = parameters.get('documentId')
operations = get_operations_by_document_id(document_id)

# Check if specific operation is available
can_create_payment = any(
    op['code'] == 'CREATE_PAYMENT' 
    for op in operations
)

result = {
    'operations': [op['code'] for op in operations],
    'can_create_payment': can_create_payment
}
```

### In UI Component

```python
from get_operations import get_document_operations

def render_document_actions(document_id):
    result = get_document_operations(document_id)
    
    if not result['success']:
        return "<div>Error loading operations</div>"
    
    state = result['state']
    operations = result['operations']
    
    html = f"<div class='document-state' style='color: {state['color_code']}'>"
    html += f"  <span>{state['name_ru']}</span>"
    html += "</div>"
    html += "<div class='document-actions'>"
    
    for op in operations:
        html += f"  <button onclick='performAction(\"{op['resource_url']}\")'>"
        html += f"    <i class='icon-{op['icon']}'></i> {op['name_ru']}"
        html += f"  </button>"
    
    html += "</div>"
    
    return html
```

## Error Handling

The module handles various error scenarios:

### Document Not Found

```python
result = get_document_operations('invalid-uuid')
# Returns:
{
    'success': False,
    'error': 'Document not found: invalid-uuid',
    'document': None,
    'state': None,
    'operations': []
}
```

### No Operations Available

```python
# Document in a state with no operations
result = get_document_operations(doc_id)
# Returns:
{
    'success': True,
    'document': {...},
    'state': {...},
    'operations': []  # Empty list
}
```

### Database Error

```python
# Connection or query error
result = get_document_operations(doc_id)
# Returns:
{
    'success': False,
    'error': 'Error getting document operations: ...',
    'document': None,
    'state': None,
    'operations': []
}
```

## Performance Considerations

The main query uses JOINs efficiently:

```sql
-- Single query to get all operations
SELECT ...
FROM swift_input si
JOIN process_operation po ON po.type_code = si.msg_type
JOIN process_operation_states pos ON pos.operation_id = po.id
JOIN process_state ps ON ps.id = pos.state_id 
    AND ps.code = si.state 
    AND ps.type_code = si.msg_type
WHERE si.id = %(document_id)s
```

**Performance characteristics:**
- Uses indexes on: `swift_input.id`, `process_operation.type_code`, `process_state.type_code+code`
- Single query for all operations
- Typically < 10ms execution time

## Testing

### Test with Sample Data

```bash
# First, find a document ID
psql -U postgres -d apng -c "SELECT id, file_name, msg_type, state FROM swift_input LIMIT 5;"

# Then test with the ID
python3 get_operations.py <document_id> -v
```

### Test All States

```python
from get_operations import get_operations_by_document_id

# Test different states
test_documents = [
    ('uuid-loaded', 'LOADED'),
    ('uuid-processed', 'PROCESSED'),
    ('uuid-payment-created', 'PAYMENT_CREATED')
]

for doc_id, expected_state in test_documents:
    ops = get_operations_by_document_id(doc_id)
    print(f"\n{expected_state}: {len(ops)} operation(s)")
    for op in ops:
        print(f"  - {op['code']}")
```

## Related Files

- `create_operations_script.py` - Creates operations in database
- `insert_operations.sql` - SQL for operations
- `queries_operations.sql` - Useful queries
- `OPERATIONS_DIAGRAM.md` - Visual documentation

## See Also

- `README_CREATE_OPERATIONS.md` - Operation creation guide
- `README-PROCESS.md` - Process management system
- `db_schema_process.sql` - Database schema

