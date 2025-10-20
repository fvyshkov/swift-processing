# Quick Start: Creating Process States

## Created Files

1. **`create_states_script.py`** - Python script for creating process states
2. **`insert_states.sql`** - SQL script for direct database insertion
3. **`README_CREATE_STATES.md`** - Detailed documentation

## States to be Created

| State Code | English | Russian | Color | Document Types | Edit/Delete |
|------------|---------|---------|-------|----------------|-------------|
| LOADED | Loaded | Загружен | 🟠 Orange (#FF8C00) | All types | ✓ Yes |
| PROCESSED | Processed | Обработан | 🔴 Burgundy (#8B0000) | All types | ✗ No |
| PAYMENT_CREATED | Payment Created | Платеж создан | 🟢 Green (#008000) | pacs.008 only | ✗ No |

## Quick Usage

### Method 1: Python Script (Recommended)

```bash
python3 create_states_script.py
```

**Advantages:**
- ✓ Automatic validation
- ✓ Detailed logging
- ✓ Error handling
- ✓ Display results

### Method 2: SQL Script

```bash
psql -U postgres -d apng -f insert_states.sql
```

**Advantages:**
- ✓ Fast execution
- ✓ Direct database access
- ✓ No Python dependencies

## Prerequisites

Before running, ensure:

1. Database schema created:
   ```bash
   psql -U postgres -d apng -f db_schema_process.sql
   ```

2. Document types populated (automatic from `ref_message_types`)

## What Gets Created

The scripts create states for these document types:
- `pacs.008` - Customer Credit Transfer (3 states)
- `pacs.009` - Financial Institution Credit Transfer (2 states)
- `camt.053` - Bank to Customer Statement (2 states)
- `camt.054` - Debit/Credit Notification (2 states)
- `camt.056` - Cancel Payment (2 states)

**Total: 11 state records**

## Verification

Check created states:

```sql
SELECT 
    type_code,
    code,
    name_combined,
    color_code,
    allow_edit,
    allow_delete
FROM process_state
ORDER BY type_code, code;
```

## More Information

See **`README_CREATE_STATES.md`** for:
- Detailed state descriptions
- Customization guide
- Integration with SWIFT processing
- Error handling details
- Database schema reference

