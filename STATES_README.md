# Process States - Complete Setup Guide

## Overview

This package provides complete tools for creating and managing process states in the SWIFT document processing system.

## 📦 What's Included

### 1. **create_states_script.py** (8.5 KB)
Python script with full automation and validation
- ✓ Automatic state creation
- ✓ Database validation
- ✓ Detailed logging
- ✓ Error handling
- ✓ Results display

**Usage**: `python3 create_states_script.py`

### 2. **insert_states.sql** (5.4 KB)
Direct SQL script for fast insertion
- ✓ Transaction-safe
- ✓ Conflict handling
- ✓ Verification queries
- ✓ Statistics

**Usage**: `psql -U postgres -d apng -f insert_states.sql`

### 3. **queries_states.sql** (8.7 KB)
20 useful SQL queries for working with states
- View states by document type
- Count documents by state
- Check permissions
- Update states
- Validate configuration
- Performance checks

### 4. **README_CREATE_STATES.md** (6.9 KB)
Complete documentation
- Detailed state descriptions
- Prerequisites
- Usage examples
- Database schema
- Integration guide
- Troubleshooting

### 5. **QUICKSTART_STATES.md** (2.1 KB)
Quick start guide
- Quick reference table
- Fast setup instructions
- Common commands

### 6. **STATES_DIAGRAM.md** (5.7 KB)
Visual documentation
- State flow diagram
- Transition rules
- Use cases
- Color reference

## 🎯 States Configuration

| State | Russian | Color | Types | Edit/Delete |
|-------|---------|-------|-------|-------------|
| **LOADED** | Загружен | 🟠 Orange | ALL | ✓ Yes |
| **PROCESSED** | Обработан | 🔴 Burgundy | ALL | ✗ No |
| **PAYMENT_CREATED** | Платеж создан | 🟢 Green | pacs.008 only | ✗ No |

## 🚀 Quick Start

### Method 1: Python (Recommended)
```bash
python3 create_states_script.py
```

### Method 2: SQL
```bash
psql -U postgres -d apng -f insert_states.sql
```

## 📋 Prerequisites

1. Database schema created:
   ```bash
   psql -U postgres -d apng -f db_schema_process.sql
   ```

2. Document types populated (automatic from `ref_message_types`)

## 📊 What Gets Created

- **11 state records** total:
  - pacs.008: 3 states (LOADED, PROCESSED, PAYMENT_CREATED)
  - pacs.009: 2 states (LOADED, PROCESSED)
  - camt.053: 2 states (LOADED, PROCESSED)
  - camt.054: 2 states (LOADED, PROCESSED)
  - camt.056: 2 states (LOADED, PROCESSED)

## 🔍 Verification

After running the script, verify:

```sql
-- Count states
SELECT COUNT(*) FROM process_state;
-- Expected: 11

-- View all states
SELECT type_code, code, name_combined, color_code 
FROM process_state 
ORDER BY type_code, code;
```

## 📖 Documentation Structure

```
QUICKSTART_STATES.md          ← Start here (2 min read)
    ↓
STATES_DIAGRAM.md             ← Visual guide (5 min read)
    ↓
README_CREATE_STATES.md       ← Complete docs (10 min read)
    ↓
queries_states.sql            ← Reference queries
```

## 🎨 Color Codes

- **🟠 #FF8C00** - Orange: Document is active and editable
- **🔴 #8B0000** - Burgundy: Document is processed and locked
- **🟢 #008000** - Green: Payment created successfully

## 🔗 Integration

States are used by:
- `swift_job_script.py` - Sets LOADED state on import
- `swift_input.state` - Stores current document state
- UI components - Display colored state indicators
- Workflow - Enforces edit/delete permissions

## 🛠️ Customization

To add new states, edit `STATES_CONFIG` in `create_states_script.py`:

```python
{
    'code': 'YOUR_STATE',
    'name_en': 'English Name',
    'name_ru': 'Русское название',
    'color_code': '#RRGGBB',
    'allow_edit': True/False,
    'allow_delete': True/False,
    'types': ['pacs.008', ...]
}
```

## 📚 Related Documentation

- `README-PROCESS.md` - Document state management system
- `db_schema_process.sql` - Database schema
- `SYSTEM_REFERENCE.md` - System architecture

## ✅ Checklist

- [ ] Database schema created (`db_schema_process.sql`)
- [ ] Document types populated
- [ ] States created (run `create_states_script.py` or `insert_states.sql`)
- [ ] Verification query executed
- [ ] Integration tested with `swift_job_script.py`

## 🆘 Troubleshooting

**Problem**: "No document types found"
- **Solution**: Run `db_schema_process.sql` first

**Problem**: "Cannot import apng_core"
- **Solution**: Make sure you're in correct Python environment

**Problem**: "Permission denied"
- **Solution**: Check database user permissions

**Problem**: "Duplicate key error"
- **Solution**: Script handles this automatically with ON CONFLICT

## 📞 Support

For issues or questions:
1. Check `README_CREATE_STATES.md` for detailed documentation
2. Review `queries_states.sql` for troubleshooting queries
3. Check logs in script output

---

**Created**: October 20, 2025  
**Version**: 1.0  
**Author**: fvyshkov@gmail.com

