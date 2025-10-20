## Quick Start: Creating Process Operations

## Overview

Creates 4 types of operations for state transitions with 14 total operation records.

## Operations Summary

| Code | Name (RU) | Icon | From → To | Types |
|------|-----------|------|-----------|-------|
| **MARK_AS_PROCESSED** | Отметить как обработанный | ✓ check | LOADED → PROCESSED | All (×5) |
| **CANCEL_PROCESSING** | Отменить обработку | ↶ undo | PROCESSED → LOADED | All (×5) |
| **CREATE_PAYMENT** | Создать платеж | 💳 payment | LOADED → PAYMENT_CREATED | pacs.008 (×1) |
| **CANCEL_PAYMENT** | Отменить создание платежа | ✕ cancel | PAYMENT_CREATED → LOADED | pacs.008 (×1) |

**Total**: 14 operations + 14 state links

## Quick Usage

### Method 1: Python (Recommended)
```bash
python3 create_operations_script.py
```

### Method 2: SQL
```bash
psql -U postgres -d apng -f insert_operations.sql
```

## Prerequisites

1. **States must exist first**:
   ```bash
   python3 create_states_script.py
   ```

2. Database schema created:
   ```bash
   psql -U postgres -d apng -f db_schema_process.sql
   ```

## What Gets Created

### By Document Type

**pacs.008** (4 operations):
- ✓ Mark as Processed
- ↶ Cancel Processing
- 💳 Create Payment
- ✕ Cancel Payment

**pacs.009, camt.053, camt.054, camt.056** (2 operations each):
- ✓ Mark as Processed
- ↶ Cancel Processing

## State Transitions

```
LOADED ──────✓──────> PROCESSED
       <─────↶───────

LOADED ──────💳─────> PAYMENT_CREATED  (pacs.008 only)
       <─────✕───────
```

## Verification

After running, verify:

```sql
-- Count operations (expected: 14)
SELECT COUNT(*) FROM process_operation;

-- View all operations
SELECT type_code, code, name_ru, icon 
FROM process_operation 
ORDER BY type_code, code;

-- Check state links (expected: 14)
SELECT COUNT(*) FROM process_operation_states;
```

## Files Created

1. **`create_operations_script.py`** - Python automation script
2. **`insert_operations.sql`** - SQL insertion script
3. **`queries_operations.sql`** - 24 useful queries
4. **`README_CREATE_OPERATIONS.md`** - Complete documentation
5. **`OPERATIONS_DIAGRAM.md`** - Visual diagrams

## More Information

See **`README_CREATE_OPERATIONS.md`** for:
- Detailed operation descriptions
- Customization guide
- Integration with UI
- Workflow examples
- Error handling

