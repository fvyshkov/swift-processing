# Execute Operation - Documentation

## Overview

Python module to execute process operations on SWIFT documents. Handles state transitions and resource URL execution.

## Features

- ✓ Execute operations by UUID or code
- ✓ Automatic state transition
- ✓ Database-specific execution
- ✓ Operation logging
- ✓ Verbose and JSON output modes
- ✓ Parameter passing

## New Operation Fields

After running the migration, operations have these additional fields:

### 1. cancel (boolean, default: false)
Indicates if this is a cancellation/reverse operation.
- `false` = Forward operation (locks document)
- `true` = Reverse operation (unlocks document)

**Examples:**
- `MARK_AS_PROCESSED`: cancel = false
- `CANCEL_PROCESSING`: cancel = true

### 2. to_state (text, nullable)
Target state code to transition to after successful execution.
- If NULL: no state change
- If set: document state will be updated

**Examples:**
- `MARK_AS_PROCESSED`: to_state = 'PROCESSED'
- `CANCEL_PROCESSING`: to_state = 'LOADED'
- `CREATE_PAYMENT`: to_state = 'PAYMENT_CREATED'

### 3. database (text, nullable)
Database connection name for operation execution.
- If NULL: use default database
- If set: execute on specified database

**Examples:**
- `database = 'default'` - main database
- `database = 'colvir_cbs'` - Colvir banking system
- `database = 'archive'` - archive database

## Installation

### Step 1: Run Migration

```bash
psql -U postgres -d apng -f migration_add_operation_fields.sql
```

This adds three new fields to `process_operation` table.

### Step 2: Update Existing Operations

```bash
psql -U postgres -d apng -f update_operations_new_fields.sql
```

This populates the new fields for existing operations.

## Usage

### 1. Command Line

#### Execute by Operation UUID

```bash
python3 execute_operation.py <document_id> <operation_uuid>
```

#### Execute by Operation Code

```bash
python3 execute_operation.py <document_id> <operation_code> -t <doc_type>
```

#### Verbose Mode

```bash
python3 execute_operation.py <document_id> MARK_AS_PROCESSED -t pacs.008 -v
```

#### JSON Output

```bash
python3 execute_operation.py <document_id> CREATE_PAYMENT -t pacs.008 -j
```

#### With Additional Parameters

```bash
python3 execute_operation.py <document_id> CREATE_PAYMENT -t pacs.008 -p account=123456 -p amount=1000
```

### 2. As Python Module

#### Simple Execution

```python
from execute_operation import execute_operation_by_code

result = execute_operation_by_code(
    operation_code='MARK_AS_PROCESSED',
    document_id='a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    doc_type='pacs.008'
)

if result['success']:
    print(f"State changed: {result['old_state']} → {result['new_state']}")
else:
    print(f"Error: {result['error']}")
```

#### With Parameters

```python
from execute_operation import execute_operation_by_code

result = execute_operation_by_code(
    operation_code='CREATE_PAYMENT',
    document_id='a1b2c3d4-...',
    doc_type='pacs.008',
    parameters={
        'debit_account': '40702810100000000001',
        'credit_account': '40702810200000000002',
        'amount': '1000.00'
    },
    verbose=True
)
```

#### Execute by UUID

```python
from execute_operation import execute_operation

result = execute_operation(
    operation_id='op-uuid-here',
    document_id='doc-uuid-here',
    verbose=True
)
```

## Return Format

```python
{
    'success': True,
    'document_id': 'uuid',
    'operation_id': 'uuid',
    'operation_code': 'MARK_AS_PROCESSED',
    'operation_name': 'Отметить как обработанный',
    'old_state': 'LOADED',
    'new_state': 'PROCESSED',
    'state_changed': True,
    'url_result': {
        'success': True,
        'action': 'markProcessed',
        'database': 'default',
        'parameters': {...},
        'message': 'Action executed successfully'
    }
}
```

## Command Line Examples

### Example 1: Mark Document as Processed

```bash
$ python3 execute_operation.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 MARK_AS_PROCESSED -t pacs.008

✓ Operation executed successfully
  Document: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  Operation: Отметить как обработанный
  State: LOADED → PROCESSED
```

### Example 2: Create Payment (Verbose)

```bash
$ python3 execute_operation.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 CREATE_PAYMENT -t pacs.008 -v

======================================================================
Operation Execution
======================================================================
Operation: Create Payment (Создать платеж)
Code: CREATE_PAYMENT
Cancel: False
Target State: PAYMENT_CREATED
Database: default

Document Information
----------------------------------------------------------------------
ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
File: pacs008_example.xml
Type: pacs.008
Current State: LOADED

Executing Operation URL
----------------------------------------------------------------------
✓ Action createPayment would be executed on database default

Updating Document State
----------------------------------------------------------------------
From: LOADED
To: PAYMENT_CREATED
✓ State updated successfully

======================================================================
Operation Completed Successfully
======================================================================
```

### Example 3: Cancel Payment

```bash
$ python3 execute_operation.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 CANCEL_PAYMENT -t pacs.008

✓ Operation executed successfully
  Document: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  Operation: Отменить создание платежа
  State: PAYMENT_CREATED → LOADED
```

### Example 4: JSON Output

```bash
$ python3 execute_operation.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 MARK_AS_PROCESSED -t pacs.008 -j
```

```json
{
  "success": true,
  "document_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "operation_id": "op-uuid",
  "operation_code": "MARK_AS_PROCESSED",
  "operation_name": "Отметить как обработанный",
  "old_state": "LOADED",
  "new_state": "PROCESSED",
  "state_changed": true,
  "url_result": {
    "success": true,
    "action": "markProcessed",
    "database": "default",
    "parameters": {
      "action": "markProcessed",
      "docId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "docType": "pacs.008"
    },
    "message": "Action markProcessed would be executed on database default"
  }
}
```

## Operation Execution Flow

```
1. Get Operation Info
   ↓
2. Get Document State
   ↓
3. Validate Operation
   ↓
4. Execute Resource URL
   ↓
5. Update Document State (if to_state is set)
   ↓
6. Log Execution
   ↓
7. Commit Transaction
```

## Integration Examples

### In Web API

```python
from flask import Flask, request, jsonify
from execute_operation import execute_operation_by_code

app = Flask(__name__)

@app.route('/api/documents/<doc_id>/operations/<op_code>', methods=['POST'])
def execute_doc_operation(doc_id, op_code):
    doc_type = request.json.get('doc_type')
    parameters = request.json.get('parameters', {})
    
    result = execute_operation_by_code(
        operation_code=op_code,
        document_id=doc_id,
        doc_type=doc_type,
        parameters=parameters
    )
    
    return jsonify(result)
```

### In BPMN Process

```python
from execute_operation import execute_operation_by_code

# In BPMN script task
document_id = parameters.get('documentId')
operation_code = parameters.get('operationCode')
doc_type = parameters.get('docType')

result = execute_operation_by_code(
    operation_code=operation_code,
    document_id=document_id,
    doc_type=doc_type,
    parameters=parameters
)

if result['success']:
    # Continue process
    result = {
        'success': True,
        'new_state': result['new_state']
    }
else:
    # Handle error
    raise Exception(result['error'])
```

### Batch Processing

```python
from execute_operation import execute_operation_by_code

# Process multiple documents
documents = [
    ('doc-uuid-1', 'pacs.008'),
    ('doc-uuid-2', 'pacs.008'),
    ('doc-uuid-3', 'camt.053')
]

results = []
for doc_id, doc_type in documents:
    result = execute_operation_by_code(
        operation_code='MARK_AS_PROCESSED',
        document_id=doc_id,
        doc_type=doc_type
    )
    results.append(result)

success_count = sum(1 for r in results if r['success'])
print(f"Processed: {success_count}/{len(results)}")
```

## Error Handling

### Document Not Found

```python
result = execute_operation_by_code('MARK_AS_PROCESSED', 'invalid-uuid', 'pacs.008')
# Returns:
{
    'success': False,
    'error': 'Document not found: invalid-uuid'
}
```

### Operation Not Found

```python
result = execute_operation_by_code('INVALID_OP', doc_id, 'pacs.008')
# Returns:
{
    'success': False,
    'error': 'Operation not found: INVALID_OP for type pacs.008'
}
```

### State Update Failed

```python
# If state update fails
{
    'success': False,
    'error': 'Failed to update document state',
    'document_id': 'uuid',
    'operation_id': 'uuid',
    'old_state': 'LOADED',
    'new_state': 'LOADED'  # No change
}
```

## Database Configuration

### Using Different Databases

Set `database` field in operation to execute on different databases:

```sql
-- Execute on Colvir banking system
UPDATE process_operation
SET database = 'colvir_cbs'
WHERE code = 'CREATE_PAYMENT';

-- Execute on archive database
UPDATE process_operation
SET database = 'archive'
WHERE code = 'ARCHIVE_DOCUMENT';
```

## Related Files

- `migration_add_operation_fields.sql` - Migration script
- `update_operations_new_fields.sql` - Update existing operations
- `get_operations.py` - Get available operations
- `create_operations_script.py` - Create operations

## See Also

- `README_GET_OPERATIONS.md` - Get operations documentation
- `README_CREATE_OPERATIONS.md` - Create operations guide
- `OPERATIONS_DIAGRAM.md` - Visual diagrams
- `README-PROCESS.md` - Process management system

