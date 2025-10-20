# Process Operations - Complete Setup Guide

## Overview

This package provides complete tools for creating and managing process operations in the SWIFT document processing system. Operations define actions that users can perform on documents, including state transitions.

## 📦 What's Included

### 1. **create_operations_script.py** (11.8 KB)
Python script with full automation and validation
- ✓ Automatic operation creation
- ✓ State validation
- ✓ Automatic state linking
- ✓ Detailed logging
- ✓ Error handling
- ✓ Results display

**Usage**: `python3 create_operations_script.py`

### 2. **insert_operations.sql** (9.5 KB)
Direct SQL script for fast insertion
- ✓ Transaction-safe
- ✓ Conflict handling
- ✓ Automatic state linking
- ✓ Verification queries
- ✓ Statistics

**Usage**: `psql -U postgres -d apng -f insert_operations.sql`

### 3. **queries_operations.sql** (12.3 KB)
24 useful SQL queries for working with operations
- View operations by document type
- Check state links
- Find available operations
- Validate configuration
- Performance checks
- State transition coverage

### 4. **README_CREATE_OPERATIONS.md** (12.5 KB)
Complete documentation
- Detailed operation descriptions
- Prerequisites
- Usage examples
- Database schema
- Integration guide
- Troubleshooting

### 5. **QUICKSTART_OPERATIONS.md** (1.8 KB)
Quick start guide
- Quick reference table
- Fast setup instructions
- Common commands

### 6. **OPERATIONS_DIAGRAM.md** (10.7 KB)
Visual documentation
- State transition diagrams
- Operation flow
- Use cases
- Icon reference
- Workflow examples

## 🎯 Operations Configuration

### Forward Operations (Lock Documents)

| Operation | Russian | Icon | From | To | Types |
|-----------|---------|------|------|-----|-------|
| **MARK_AS_PROCESSED** | Отметить как обработанный | ✓ check | LOADED | PROCESSED | All (5) |
| **CREATE_PAYMENT** | Создать платеж | 💳 payment | LOADED | PAYMENT_CREATED | pacs.008 (1) |

### Reverse Operations (Unlock Documents)

| Operation | Russian | Icon | From | To | Types |
|-----------|---------|------|------|-----|-------|
| **CANCEL_PROCESSING** | Отменить обработку | ↶ undo | PROCESSED | LOADED | All (5) |
| **CANCEL_PAYMENT** | Отменить создание платежа | ✕ cancel | PAYMENT_CREATED | LOADED | pacs.008 (1) |

**Total Records**: 14 operations + 14 state links

## 🚀 Quick Start

### Prerequisites

**IMPORTANT**: Create states first!

```bash
# Method 1: Python
python3 create_states_script.py

# Method 2: SQL
psql -U postgres -d apng -f insert_states.sql
```

### Create Operations

**Method 1: Python (Recommended)**
```bash
python3 create_operations_script.py
```

**Method 2: SQL**
```bash
psql -U postgres -d apng -f insert_operations.sql
```

## 📊 What Gets Created

### By Document Type

| Type | MARK_AS_PROCESSED | CANCEL_PROCESSING | CREATE_PAYMENT | CANCEL_PAYMENT | Total |
|------|-------------------|-------------------|----------------|----------------|-------|
| **pacs.008** | ✓ | ✓ | ✓ | ✓ | 4 |
| **pacs.009** | ✓ | ✓ | - | - | 2 |
| **camt.053** | ✓ | ✓ | - | - | 2 |
| **camt.054** | ✓ | ✓ | - | - | 2 |
| **camt.056** | ✓ | ✓ | - | - | 2 |
| **TOTAL** | **5** | **5** | **1** | **1** | **14** |

### State Links

Each operation is linked to state(s) where it's available:

| Operation | Linked To State | Count |
|-----------|----------------|-------|
| MARK_AS_PROCESSED | LOADED | 5 |
| CANCEL_PROCESSING | PROCESSED | 5 |
| CREATE_PAYMENT | LOADED | 1 |
| CANCEL_PAYMENT | PAYMENT_CREATED | 1 |
| **TOTAL** | | **14** |

## 🔍 Verification

After running the script, verify:

```sql
-- Count operations (expected: 14)
SELECT COUNT(*) FROM process_operation;

-- Count state links (expected: 14)
SELECT COUNT(*) FROM process_operation_states;

-- View all operations with states
SELECT 
    po.type_code,
    po.code,
    po.name_ru,
    STRING_AGG(ps.code, ', ') as available_in_states
FROM process_operation po
LEFT JOIN process_operation_states pos ON pos.operation_id = po.id
LEFT JOIN process_state ps ON ps.id = pos.state_id
GROUP BY po.type_code, po.code, po.name_ru
ORDER BY po.type_code, po.code;
```

## 📖 Documentation Structure

```
QUICKSTART_OPERATIONS.md          ← Start here (2 min read)
    ↓
OPERATIONS_DIAGRAM.md             ← Visual guide (7 min read)
    ↓
README_CREATE_OPERATIONS.md       ← Complete docs (15 min read)
    ↓
queries_operations.sql            ← Reference queries
```

## 🔗 State Transitions

### All Document Types (pacs.009, camt.053, camt.054, camt.056)

```
🟠 LOADED ──[✓ Mark as Processed]──> 🔴 PROCESSED
          <─[↶ Cancel Processing]──
```

### pacs.008 Only (Customer Credit Transfer)

```
                    [✓ Mark as Processed]
🟠 LOADED ────────────────────────────────────> 🔴 PROCESSED
    │                                               │
    │                                               │
    │ [💳 Create Payment]          [↶ Cancel Processing]
    │                                               │
    ▼                                               │
🟢 PAYMENT_CREATED ─────────────────────────────────┘
    │
    │ [✕ Cancel Payment]
    │
    └──────────────────────> 🟠 LOADED
```

## 🎨 Icon Reference

| Icon | Symbol | Meaning | Operations |
|------|--------|---------|------------|
| `check` | ✓ | Approve/Complete | MARK_AS_PROCESSED |
| `undo` | ↶ | Reverse/Cancel | CANCEL_PROCESSING |
| `payment` | 💳 | Create Payment | CREATE_PAYMENT |
| `cancel` | ✕ | Cancel Action | CANCEL_PAYMENT |

## 💡 Use Cases

### Use Case 1: Standard Processing (All Types)

**Scenario**: Mark camt.053 statement as processed

1. Document arrives → LOADED (orange, unlocked)
2. User reviews document
3. User clicks **[✓ Mark as Processed]**
4. Document → PROCESSED (burgundy, locked)
5. If needed: User clicks **[↶ Cancel Processing]**
6. Document → LOADED (orange, unlocked)

### Use Case 2: Payment Creation (pacs.008 only)

**Scenario**: Create payment from pacs.008 message

1. Payment message arrives → LOADED (orange, unlocked)
2. User clicks **[💳 Create Payment]**
3. Form opens: Select Debit/Credit accounts from АБС
4. User fills payment details
5. Payment created in core banking system
6. Document → PAYMENT_CREATED (green, locked)
7. If error: User clicks **[✕ Cancel Payment]**
8. Payment cancelled, Document → LOADED (orange, unlocked)

## 🔧 Integration with UI

Operations appear as buttons in the UI based on:

### Visibility Rules

1. **Document Type Match**: Only show operations for current document type
2. **State Match**: Only show operations available in current state
3. **Permissions**: Check user permissions (if implemented)

### Example: pacs.008 Document

**In LOADED state:**
- Shows: [✓ Mark as Processed] [💳 Create Payment]

**In PROCESSED state:**
- Shows: [↶ Cancel Processing]

**In PAYMENT_CREATED state:**
- Shows: [✕ Cancel Payment]

## 📊 Database Structure

### Tables Involved

```
process_type (5 records)
    ↓
process_operation (14 records)
    ↓
process_operation_states (14 links)
    ↓
process_state (11 records)
```

### Resource URL Pattern

```
/aoa/ProcessAction?action={actionName}&docId={id}&docType={type}
```

Parameters:
- `{id}` - Document UUID (replaced at runtime)
- `{type}` - Document type code (replaced at runtime)
- `{actionName}` - Action to perform

## 🛠️ Customization

### Adding New Operation

Edit `OPERATIONS_CONFIG` in `create_operations_script.py`:

```python
{
    'code': 'APPROVE_PAYMENT',
    'name_en': 'Approve Payment',
    'name_ru': 'Утвердить платеж',
    'icon': 'thumbs-up',
    'resource_url': '/aoa/ProcessAction?action=approvePayment&docId={id}&docType={type}',
    'types': ['pacs.008'],
    'available_in_states': ['LOADED'],
    'target_state': 'APPROVED'
}
```

Then create the new state first!

## 🆘 Troubleshooting

**Problem**: "No states found in process_state table"
- **Solution**: Run `create_states_script.py` first

**Problem**: "State [code] not found for type [type]"
- **Solution**: Verify states exist for that document type

**Problem**: "Cannot import apng_core"
- **Solution**: Check Python environment

**Problem**: "No operations showing in UI"
- **Solution**: Check state links in `process_operation_states` table

## ✅ Checklist

- [ ] Database schema created (`db_schema_process.sql`)
- [ ] Document types populated
- [ ] **States created** (`create_states_script.py` or `insert_states.sql`)
- [ ] **Operations created** (`create_operations_script.py` or `insert_operations.sql`)
- [ ] Verification queries executed
- [ ] UI tested with sample documents
- [ ] Workflow handlers implemented

## 📚 Related Files

### Required First (Dependencies)
- `db_schema_process.sql` - Database schema
- `create_states_script.py` - Create states first!
- `insert_states.sql` - SQL alternative for states

### This Package
- `create_operations_script.py` - Python script
- `insert_operations.sql` - SQL script
- `queries_operations.sql` - Useful queries
- `README_CREATE_OPERATIONS.md` - Full documentation
- `OPERATIONS_DIAGRAM.md` - Visual diagrams
- `QUICKSTART_OPERATIONS.md` - Quick start

### Related Documentation
- `README-PROCESS.md` - Process management system
- `STATES_DIAGRAM.md` - States reference
- `STATES_README.md` - States overview

## 🚧 Next Steps

After creating operations:

1. **Test in UI**: Verify buttons appear correctly
2. **Implement Handlers**: Create workflow for each resource URL
3. **Add Permissions**: Restrict operations by user role
4. **Setup Logging**: Track operation execution
5. **Create History**: Record all operation executions
6. **Add Validations**: Business rules for each operation

---

**Created**: October 20, 2025  
**Version**: 1.0  
**Author**: fvyshkov@gmail.com

