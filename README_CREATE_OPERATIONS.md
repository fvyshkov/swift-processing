# Process Operations Creation Script

## Overview

This script creates process operations for SWIFT document processing system. Operations define actions that can be performed on documents, including state transitions.

## Operations Configuration

The script creates **4 types of operations** with **14 total operation records**.

### 1. MARK_AS_PROCESSED (Отметить как обработанный)

**Forward operation: LOADED → PROCESSED**

- **English name**: Mark as Processed
- **Russian name**: Отметить как обработанный
- **Icon**: `check` ✓
- **Available in**: LOADED state
- **Target state**: PROCESSED
- **Document types**: ALL (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- **Records created**: 5 (one per document type)

Marks document as processed after validation. Document becomes locked (no editing/deletion).

### 2. CANCEL_PROCESSING (Отменить обработку)

**Reverse operation: PROCESSED → LOADED**

- **English name**: Cancel Processing
- **Russian name**: Отменить обработку
- **Icon**: `undo` ↶
- **Available in**: PROCESSED state
- **Target state**: LOADED
- **Document types**: ALL (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- **Records created**: 5 (one per document type)

Reverts processed document back to editable state. Document becomes unlocked.

### 3. CREATE_PAYMENT (Создать платеж)

**Forward operation: LOADED → PAYMENT_CREATED** *(pacs.008 only)*

- **English name**: Create Payment
- **Russian name**: Создать платеж
- **Icon**: `payment` 💳
- **Available in**: LOADED state
- **Target state**: PAYMENT_CREATED
- **Document types**: ONLY pacs.008 (Customer Credit Transfer)
- **Records created**: 1

Creates payment in core banking system based on pacs.008 message. Opens form for account selection.

### 4. CANCEL_PAYMENT (Отменить создание платежа)

**Reverse operation: PAYMENT_CREATED → LOADED** *(pacs.008 only)*

- **English name**: Cancel Payment Creation
- **Russian name**: Отменить создание платежа
- **Icon**: `cancel` ✕
- **Available in**: PAYMENT_CREATED state
- **Target state**: LOADED
- **Document types**: ONLY pacs.008 (Customer Credit Transfer)
- **Records created**: 1

Cancels payment creation and reverts document to editable state.

---

## Prerequisites

Before running this script, ensure:

1. **Database schema created**:
   ```bash
   psql -U postgres -d apng -f db_schema_process.sql
   ```

2. **Process states created**:
   ```bash
   python3 create_states_script.py
   # OR
   psql -U postgres -d apng -f insert_states.sql
   ```

3. **Required Python modules** (for Python script):
   - `apng_core.db`
   - `apng_core.logger`

---

## Usage

### Method 1: Python Script (Recommended)

Run the script:

```bash
python3 create_operations_script.py
```

**Advantages:**
- ✓ Automatic validation
- ✓ Checks for required states
- ✓ Detailed logging
- ✓ Error handling
- ✓ Display results with state links

**Output Example:**
```
======================================================================
Starting process operations creation
======================================================================

Available states by document type:
  - camt.053: 2 states
  - camt.054: 2 states
  - pacs.008: 3 states
  - pacs.009: 2 states

Creating process operations...

Processing operation: Mark as Processed (Отметить как обработанный)
  Code: MARK_AS_PROCESSED
  Icon: check
  Available in states: LOADED
  Target state: PROCESSED
  Document types: pacs.008, pacs.009, camt.053, camt.054, camt.056
    ✓ Created/updated for pacs.008: a1b2c3d4-...
    ✓ Linked to 1 state(s)
    ✓ Created/updated for pacs.009: e5f6g7h8-...
    ✓ Linked to 1 state(s)
    ...

======================================================================
Process operations creation completed
  Created/Updated operations: 14
  State links created: 14
  Errors: 0
======================================================================
```

### Method 2: SQL Script

Run the SQL script:

```bash
psql -U postgres -d apng -f insert_operations.sql
```

**Advantages:**
- ✓ Fast execution
- ✓ Direct database access
- ✓ No Python dependencies
- ✓ Transaction-safe

---

## What Gets Created

### Total Records: 14 operations + 14 state links

| Operation | Types | Count | Total |
|-----------|-------|-------|-------|
| MARK_AS_PROCESSED | All 5 types | × 5 | 5 |
| CANCEL_PROCESSING | All 5 types | × 5 | 5 |
| CREATE_PAYMENT | pacs.008 only | × 1 | 1 |
| CANCEL_PAYMENT | pacs.008 only | × 1 | 1 |
| **TOTAL** | | | **14** |

### State Links Created: 14

Each operation is linked to the state(s) where it's available:
- MARK_AS_PROCESSED → linked to LOADED state (5 links)
- CANCEL_PROCESSING → linked to PROCESSED state (5 links)
- CREATE_PAYMENT → linked to LOADED state (1 link)
- CANCEL_PAYMENT → linked to PAYMENT_CREATED state (1 link)

---

## Database Schema

### process_operation Table

```sql
CREATE TABLE process_operation (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    type_code text NOT NULL,              -- FK to process_type
    code text NOT NULL,                   -- Operation code
    name_en text NOT NULL,                -- English name
    name_ru text NOT NULL,                -- Russian name
    name_combined text NOT NULL,          -- Combined display name
    icon text,                            -- Icon identifier
    resource_url text,                    -- URL to execute operation
    availability_condition text,          -- JSON: available states & target
    
    PRIMARY KEY (id),
    UNIQUE (type_code, code),
    FOREIGN KEY (type_code) REFERENCES process_type (code)
);
```

### process_operation_states Table

```sql
CREATE TABLE process_operation_states (
    operation_id uuid NOT NULL,           -- FK to process_operation
    state_id uuid NOT NULL,               -- FK to process_state
    
    PRIMARY KEY (operation_id, state_id),
    FOREIGN KEY (operation_id) REFERENCES process_operation (id),
    FOREIGN KEY (state_id) REFERENCES process_state (id)
);
```

---

## Verification

After running the script, verify operations were created:

### Check operation count
```sql
SELECT COUNT(*) FROM process_operation;
-- Expected: 14
```

### View all operations
```sql
SELECT 
    type_code,
    code,
    name_combined,
    icon
FROM process_operation 
ORDER BY type_code, code;
```

### View operations with state links
```sql
SELECT 
    po.type_code,
    po.code,
    po.name_ru,
    STRING_AGG(ps.code, ', ' ORDER BY ps.code) as available_in_states
FROM process_operation po
LEFT JOIN process_operation_states pos ON pos.operation_id = po.id
LEFT JOIN process_state ps ON ps.id = pos.state_id
GROUP BY po.type_code, po.code, po.name_ru
ORDER BY po.type_code, po.code;
```

### Check state links count
```sql
SELECT COUNT(*) FROM process_operation_states;
-- Expected: 14
```

---

## Operation Details

### Availability Condition Format

Each operation has an `availability_condition` field containing JSON:

```json
{
    "target_state": "PROCESSED",
    "available_in_states": ["LOADED"]
}
```

This defines:
- **target_state**: State document will transition to after operation
- **available_in_states**: States where this operation button should appear

---

## Resource URL Format

Resource URLs use placeholders for dynamic values:

```
/aoa/ProcessAction?action=markProcessed&docId={id}&docType={type}
```

Placeholders:
- `{id}` - Document UUID
- `{type}` - Document type code (pacs.008, etc.)

These are replaced at runtime by the UI framework.

---

## Customization

To add new operations, edit `OPERATIONS_CONFIG` in `create_operations_script.py`:

```python
{
    'code': 'YOUR_OPERATION_CODE',
    'name_en': 'English Name',
    'name_ru': 'Русское название',
    'icon': 'icon_name',
    'resource_url': '/aoa/ProcessAction?action=yourAction&docId={id}&docType={type}',
    'types': ['pacs.008', ...],           # Document types
    'available_in_states': ['LOADED'],    # Available in these states
    'target_state': 'NEW_STATE'           # Target state after operation
}
```

---

## Integration with UI

Operations are displayed in the UI based on:

1. **Document type**: Only operations for current document type are shown
2. **Current state**: Only operations available in current state are shown
3. **Icon**: Displayed as button icon
4. **Name**: Button label (combined EN/RU)

### Example: pacs.008 Document

**When in LOADED state**, user sees:
- [✓] Mark as Processed
- [💳] Create Payment

**When in PROCESSED state**, user sees:
- [↶] Cancel Processing

**When in PAYMENT_CREATED state**, user sees:
- [✕] Cancel Payment

---

## Error Handling

The script includes comprehensive error handling:

### Common Issues

**Problem**: "No states found in process_state table"
- **Solution**: Run `create_states_script.py` first

**Problem**: "Cannot import apng_core modules"
- **Solution**: Ensure correct Python environment

**Problem**: "Skipping [type] - no states found"
- **Solution**: Verify states exist for that document type

**Problem**: "State [code] not found for type [type]"
- **Solution**: Check state configuration in `create_states_script.py`

---

## Workflow Integration

Operations integrate with the BPMN workflow engine:

1. **User clicks operation button** in UI
2. **Resource URL called** with document ID and type
3. **BPMN process starts** (may include):
   - User tasks (forms for data entry)
   - Service tasks (automatic operations)
   - State transitions
4. **Document state updated** to target_state
5. **Audit trail recorded** in operation history

---

## See Also

- `OPERATIONS_DIAGRAM.md` - Visual operation flow diagrams
- `insert_operations.sql` - SQL script for operations
- `queries_operations.sql` - Useful SQL queries
- `create_states_script.py` - Create required states first
- `README-PROCESS.md` - Document state management system
- `db_schema_process.sql` - Database schema

---

## Next Steps

After creating operations:

1. **Test operations** in UI
2. **Implement workflow handlers** for resource URLs
3. **Configure permissions** for operations
4. **Setup audit logging** for operation execution
5. **Create custom operations** as needed

---

**Created**: October 20, 2025  
**Version**: 1.0  
**Author**: fvyshkov@gmail.com

