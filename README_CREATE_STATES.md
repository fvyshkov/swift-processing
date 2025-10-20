# Process States Creation Script

## Overview

This script creates process states for SWIFT document processing system. It populates the `process_state` table with predefined states for different document types.

## States Configuration

The script creates the following states:

### 1. LOADED (Загружен)
- **English name**: Loaded
- **Russian name**: Загружен
- **Color**: `#FF8C00` (Orange / DarkOrange)
- **Allow edit**: Yes
- **Allow delete**: Yes
- **Document types**: ALL (`pacs.008`, `pacs.009`, `camt.053`, `camt.054`, `camt.056`)

This state is assigned when a document is initially imported into the system.

### 2. PROCESSED (Обработан)
- **English name**: Processed
- **Russian name**: Обработан
- **Color**: `#8B0000` (Burgundy / DarkRed)
- **Allow edit**: No
- **Allow delete**: No
- **Document types**: ALL (`pacs.008`, `pacs.009`, `camt.053`, `camt.054`, `camt.056`)

This state indicates that the document has been processed and should not be modified or deleted.

### 3. PAYMENT_CREATED (Платеж создан)
- **English name**: Payment Created
- **Russian name**: Платеж создан
- **Color**: `#008000` (Green)
- **Allow edit**: No
- **Allow delete**: No
- **Document types**: ONLY `pacs.008`

This state is specific to pacs.008 documents and indicates that a payment has been created in the banking system.

## Prerequisites

Before running this script, ensure:

1. Database schema is created:
   ```bash
   psql -U postgres -d apng -f db_schema_process.sql
   ```

2. Document types exist in `process_type` table (automatically populated from `ref_message_types`)

3. Required Python modules are available:
   - `apng_core.db`
   - `apng_core.logger`

## Usage

Run the script:

```bash
python3 create_states_script.py
```

Or make it executable and run directly:

```bash
chmod +x create_states_script.py
./create_states_script.py
```

## What the Script Does

1. **Checks document types**: Verifies that required document types exist in `process_type` table
2. **Creates states**: Inserts or updates states in `process_state` table
3. **Handles conflicts**: Uses `ON CONFLICT DO UPDATE` to avoid duplicate errors
4. **Logs progress**: Provides detailed output of all operations
5. **Displays results**: Shows all created states grouped by document type

## Output Example

```
======================================================================
Starting process states creation
======================================================================

Available document types:
  - camt.053: Bank to Customer Statement (Банковская выписка клиенту)
  - camt.054: Bank to Customer Debit/Credit Notification (Уведомление о дебете/кредите)
  - pacs.008: Customer Credit Transfer (Клиентский кредитовый перевод)
  - pacs.009: Financial Institution Credit Transfer (COV) (Межбанковский кредитовый перевод (покрытие))

Creating process states...

Processing state: Loaded (Загружен)
  Code: LOADED
  Color: #FF8C00
  Allow edit: True
  Allow delete: True
  Document types: pacs.008, pacs.009, camt.053, camt.054, camt.056
    ✓ Created/updated for pacs.008: a1b2c3d4-...
    ✓ Created/updated for pacs.009: e5f6g7h8-...
    ✓ Created/updated for camt.053: i9j0k1l2-...
    ✓ Created/updated for camt.054: m3n4o5p6-...

Processing state: Processed (Обработан)
  Code: PROCESSED
  Color: #8B0000
  Allow edit: False
  Allow delete: False
  Document types: pacs.008, pacs.009, camt.053, camt.054, camt.056
    ✓ Created/updated for pacs.008: q7r8s9t0-...
    ...

Processing state: Payment Created (Платеж создан)
  Code: PAYMENT_CREATED
  Color: #008000
  Allow edit: False
  Allow delete: False
  Document types: pacs.008
    ✓ Created/updated for pacs.008: u1v2w3x4-...

======================================================================
Process states creation completed
  Created/Updated: 13
  Errors: 0
======================================================================

Current states in database:

camt.053:
  - LOADED: Loaded (Загружен)
      Color: #FF8C00, Edit: True, Delete: True
  - PROCESSED: Processed (Обработан)
      Color: #8B0000, Edit: False, Delete: False

camt.054:
  - LOADED: Loaded (Загружен)
      Color: #FF8C00, Edit: True, Delete: True
  - PROCESSED: Processed (Обработан)
      Color: #8B0000, Edit: False, Delete: False

pacs.008:
  - LOADED: Loaded (Загружен)
      Color: #FF8C00, Edit: True, Delete: True
  - PAYMENT_CREATED: Payment Created (Платеж создан)
      Color: #008000, Edit: False, Delete: False
  - PROCESSED: Processed (Обработан)
      Color: #8B0000, Edit: False, Delete: False

pacs.009:
  - LOADED: Loaded (Загружен)
      Color: #FF8C00, Edit: True, Delete: True
  - PROCESSED: Processed (Обработан)
      Color: #8B0000, Edit: False, Delete: False
```

## Database Structure

States are stored in the `process_state` table with the following schema:

```sql
CREATE TABLE process_state (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    type_code text NOT NULL,                 -- FK to process_type
    code text NOT NULL,                      -- State code (LOADED, PROCESSED, etc.)
    name_en text NOT NULL,                   -- English name
    name_ru text NOT NULL,                   -- Russian name
    name_combined text NOT NULL,             -- Combined display name
    color_code text,                         -- Hex color code (#RRGGBB)
    allow_edit boolean DEFAULT false,        -- Allow document editing
    allow_delete boolean DEFAULT false,      -- Allow document deletion
    
    CONSTRAINT process_state_type_code_unique UNIQUE (type_code, code)
);
```

## Customization

To add new states or modify existing ones, edit the `STATES_CONFIG` list in the script:

```python
STATES_CONFIG = [
    {
        'code': 'YOUR_STATE_CODE',
        'name_en': 'English Name',
        'name_ru': 'Русское название',
        'color_code': '#RRGGBB',  # Hex color
        'allow_edit': True/False,
        'allow_delete': True/False,
        'types': ['pacs.008', ...]  # List of document types
    },
    # ... more states
]
```

## Error Handling

The script includes comprehensive error handling:
- Checks for database connectivity
- Validates document types existence
- Handles SQL conflicts gracefully
- Provides detailed error messages and stack traces

## Integration with SWIFT Processing

These states are used by:
- `swift_job_script.py` - Sets initial LOADED state on import
- `swift_input` table - Stores current state in `state` field
- UI components - Display states with configured colors
- Workflow processes - Control document lifecycle based on states

## See Also

- `README-PROCESS.md` - Document state management system overview
- `db_schema_process.sql` - Database schema for process management
- `swift_job_script.py` - Main SWIFT processing job

