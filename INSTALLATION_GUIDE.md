# SWIFT Process Management System - Complete Installation Guide

## Overview

Complete system for managing SWIFT document states, operations, and state transitions.

## System Components

### 1. States (11 records)
- LOADED (Загружен) - Orange, editable
- PROCESSED (Обработан) - Burgundy, locked
- PAYMENT_CREATED (Платеж создан) - Green, locked [pacs.008 only]

### 2. Operations (14 records)
- MARK_AS_PROCESSED → PROCESSED
- CANCEL_PROCESSING → LOADED
- CREATE_PAYMENT → PAYMENT_CREATED [pacs.008 only]
- CANCEL_PAYMENT → LOADED [pacs.008 only]

### 3. Execution Engine
- Get available operations for document
- Execute operations with state changes
- Database-specific operation execution

## Complete Installation

### Prerequisites

```bash
# Ensure database and schema exist
psql -U postgres -d apng -c "\dt"
```

### Step 1: Create Schema

```bash
cd /Users/fvyshkov/PROJECTS/swift-processing

# Create process management tables
psql -U postgres -d apng -f db_schema_process.sql
```

**Creates:**
- `process_type` - Document types (5 records)
- `process_state` - Document states (empty)
- `process_operation` - Operations (empty)
- `process_operation_states` - Links (empty)

### Step 2: Create States

**Option A: Python (recommended)**
```bash
python3 create_states_script.py
```

**Option B: SQL**
```bash
psql -U postgres -d apng -f insert_states.sql
```

**Result:** 11 state records created

### Step 3: Create Operations

**Option A: Python (recommended)**
```bash
python3 create_operations_script.py
```

**Option B: SQL**
```bash
psql -U postgres -d apng -f insert_operations.sql
```

**Result:** 14 operation records + 14 state links created

### Step 4: Add Operation Fields (Migration)

```bash
# Add cancel, to_state, database fields
psql -U postgres -d apng -f migration_add_operation_fields.sql

# Update existing operations with new field values
psql -U postgres -d apng -f update_operations_new_fields.sql
```

**Result:** 3 new fields added and populated

### Step 5: Verify Installation

```bash
# Check states
psql -U postgres -d apng -c "SELECT COUNT(*) FROM process_state;"
# Expected: 11

# Check operations
psql -U postgres -d apng -c "SELECT COUNT(*) FROM process_operation;"
# Expected: 14

# Check operation-state links
psql -U postgres -d apng -c "SELECT COUNT(*) FROM process_operation_states;"
# Expected: 14

# View operations with new fields
psql -U postgres -d apng -c "
SELECT code, cancel, to_state, database 
FROM process_operation 
ORDER BY type_code, code 
LIMIT 5;
"
```

## Usage Examples

### 1. Get Available Operations

```bash
# Get first document ID
DOC_ID=$(psql -U postgres -d apng -t -c "SELECT id FROM swift_input WHERE msg_type='pacs.008' LIMIT 1;")

# Get available operations
python3 get_operations.py $DOC_ID -v
```

### 2. Execute Operation

```bash
# Mark as processed
python3 execute_operation.py $DOC_ID MARK_AS_PROCESSED -t pacs.008 -v

# Create payment
python3 execute_operation.py $DOC_ID CREATE_PAYMENT -t pacs.008 -v

# Cancel payment
python3 execute_operation.py $DOC_ID CANCEL_PAYMENT -t pacs.008 -v

# Cancel processing
python3 execute_operation.py $DOC_ID CANCEL_PROCESSING -t pacs.008 -v
```

### 3. Python Integration

```python
from get_operations import get_operations_by_document_id
from execute_operation import execute_operation_by_code

# Get available operations
document_id = "your-uuid-here"
operations = get_operations_by_document_id(document_id)

for op in operations:
    print(f"{op['icon']} {op['name_ru']}")

# Execute operation
result = execute_operation_by_code(
    operation_code='MARK_AS_PROCESSED',
    document_id=document_id,
    doc_type='pacs.008'
)

if result['success']:
    print(f"State: {result['old_state']} → {result['new_state']}")
```

## File Reference

### SQL Scripts (7 files)
```
db_schema_process.sql              - Schema creation
insert_states.sql                  - Insert states
insert_operations.sql              - Insert operations
migration_add_operation_fields.sql - Add new operation fields
update_operations_new_fields.sql   - Update operations
queries_states.sql                 - State queries (20)
queries_operations.sql             - Operation queries (24)
```

### Python Scripts (4 files)
```
create_states_script.py            - Create states
create_operations_script.py        - Create operations
get_operations.py                  - Get available operations
execute_operation.py               - Execute operations
```

### Documentation (8 files)
```
STATES_README.md                   - States overview
STATES_DIAGRAM.md                  - State diagrams
QUICKSTART_STATES.md               - States quick start
README_CREATE_STATES.md            - States creation guide

OPERATIONS_README.md               - Operations overview
OPERATIONS_DIAGRAM.md              - Operation diagrams
QUICKSTART_OPERATIONS.md           - Operations quick start
README_CREATE_OPERATIONS.md        - Operations creation guide

README_GET_OPERATIONS.md           - Get operations guide
README_EXECUTE_OPERATION.md        - Execute operations guide

README-PROCESS.md                  - System architecture
```

## Database Schema

### Tables Created

```sql
process_type (5 records)
  ├─ code (PK)
  ├─ name_en, name_ru, name_combined
  └─ resource_url

process_state (11 records)
  ├─ id (PK, UUID)
  ├─ type_code (FK → process_type)
  ├─ code
  ├─ name_en, name_ru, name_combined
  ├─ color_code
  ├─ allow_edit
  └─ allow_delete

process_operation (14 records)
  ├─ id (PK, UUID)
  ├─ type_code (FK → process_type)
  ├─ code
  ├─ name_en, name_ru, name_combined
  ├─ icon
  ├─ resource_url
  ├─ availability_condition (JSON)
  ├─ cancel (boolean) ← NEW
  ├─ to_state (text) ← NEW
  └─ database (text) ← NEW

process_operation_states (14 records)
  ├─ operation_id (FK → process_operation)
  └─ state_id (FK → process_state)
```

## State Transition Matrix

### All Document Types (pacs.009, camt.053, camt.054, camt.056)

| From State | Operation | To State |
|------------|-----------|----------|
| LOADED | MARK_AS_PROCESSED | PROCESSED |
| PROCESSED | CANCEL_PROCESSING | LOADED |

### pacs.008 Only

| From State | Operation | To State |
|------------|-----------|----------|
| LOADED | MARK_AS_PROCESSED | PROCESSED |
| LOADED | CREATE_PAYMENT | PAYMENT_CREATED |
| PROCESSED | CANCEL_PROCESSING | LOADED |
| PAYMENT_CREATED | CANCEL_PAYMENT | LOADED |

## Quick Commands

### Installation
```bash
psql -U postgres -d apng -f db_schema_process.sql
python3 create_states_script.py
python3 create_operations_script.py
psql -U postgres -d apng -f migration_add_operation_fields.sql
psql -U postgres -d apng -f update_operations_new_fields.sql
```

### Verification
```bash
psql -U postgres -d apng -c "
SELECT 'States' as table, COUNT(*) FROM process_state
UNION ALL
SELECT 'Operations', COUNT(*) FROM process_operation
UNION ALL
SELECT 'Links', COUNT(*) FROM process_operation_states;
"
```

### Usage
```bash
python3 get_operations.py <document_id>
python3 execute_operation.py <document_id> <operation_code> -t <doc_type>
```

## Troubleshooting

### Problem: States not created
```bash
# Solution: Check if process_type table has data
psql -U postgres -d apng -c "SELECT * FROM process_type;"
```

### Problem: Operations not showing
```bash
# Solution: Check state links
psql -U postgres -d apng -c "
SELECT po.code, ps.code as state
FROM process_operation po
JOIN process_operation_states pos ON pos.operation_id = po.id
JOIN process_state ps ON ps.id = pos.state_id
LIMIT 10;
"
```

### Problem: Migration failed
```bash
# Solution: Check if columns already exist
psql -U postgres -d apng -c "\d process_operation"
```

## Next Steps

1. **Test with sample documents**
   - Import test documents
   - Get available operations
   - Execute state transitions

2. **Implement workflow handlers**
   - Create BPMN processes for operations
   - Implement resource URL endpoints
   - Add business logic validation

3. **Setup audit logging**
   - Create operation_history table
   - Log all operation executions
   - Track state changes

4. **Configure UI**
   - Display state colors
   - Show operation buttons
   - Handle operation execution

5. **Add permissions**
   - User role management
   - Operation-level permissions
   - State-based access control

---

**Version**: 1.0  
**Created**: October 20, 2025  
**Author**: fvyshkov@gmail.com

