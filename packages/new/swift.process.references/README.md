# SWIFT Process References Package

## Description

This package provides three reference objects (справочники) for the SWIFT document state management system. These are read-only reference tables that can be used in other forms via SelectEdit controls.

## Prerequisites

**IMPORTANT**: Before installing this package, you must create the database objects using:

Execute the file: `db_schema_process.sql`

This creates four tables:
- `process_type` - Document types reference
- `process_state` - Document states with colors and permissions
- `process_operation` - Available operations for documents
- `process_operation_states` - Many-to-many relation between operations and states

The schema also pre-populates `process_type` with data from `ref_message_types` table (5 SWIFT message types).

## Features

### Three Reference Objects

#### 1. processType - Document Types Reference
- **Table**: `process_type`
- **Key field**: `code` (text)
- **Columns**: code, name_en, name_ru, name_combined, resource_url
- **Filter**: by code and name
- **Usage**: Base reference for document type selection

#### 2. processState - Document States Reference
- **Table**: `process_state`
- **Key field**: `id` (UUID)
- **Columns**: type_code, code, name_en, name_ru, name_combined, color_code, allow_edit, allow_delete
- **Filter**: by document type (uses processType reference), state code, name
- **Usage**: Reference for state selection, filtered by document type

#### 3. processOperation - Document Operations Reference
- **Table**: `process_operation` (JOIN with `process_operation_states`)
- **Key field**: `id` (UUID)
- **Columns**: type_code, code, name_en, name_ru, name_combined, icon, states (aggregated), resource_url
- **Filter**: by document type (uses processType reference), operation code, name
- **Usage**: Reference for operation selection with visible related states

## Installation

1. **Create the database tables**:
   ```bash
   psql -U postgres -d your_database -f db_schema_process.sql
   ```

2. **Verify initial data**:
   ```sql
   SELECT * FROM process_type;
   -- Should show 5 SWIFT message types
   ```

3. **Archive the package**:
   ```bash
   cd packages/new/swift.process.references
   zip -r ../swift.process.references.zip ao/ .configs/ .package.info README.md
   ```

4. **Upload** the `swift.process.references.zip` file through the package manager interface

## Structure

```
swift.process.references/
├── ao/
│   ├── processType.json         # Document types reference
│   ├── processState.json        # Document states reference
│   └── processOperation.json    # Document operations reference
├── .configs/
│   └── aoa.Object.xml           # Object registration (3 objects)
├── .package.info                # Package metadata
└── README.md                    # This file
```

## Usage in Other Forms

These reference objects are designed to be used in SelectEdit controls:

### Example 1: Select Document Type
```json
{
  "type_code": {
    "label": "Document Type",
    "control": "SelectEdit",
    "controlProps": {
      "object": "processType",
      "method": "getItemList",
      "valueField": "code",
      "displayField": "name_combined"
    }
  }
}
```

### Example 2: Select State (filtered by type)
```json
{
  "state_id": {
    "label": "Document State",
    "control": "SelectEdit",
    "controlProps": {
      "object": "processState",
      "method": "getItemList",
      "valueField": "id",
      "displayField": "name_combined",
      "filterField": "type_code",
      "filterValue$": "mem.type_code"
    }
  }
}
```

### Example 3: Select Operation (filtered by type)
```json
{
  "operation_id": {
    "label": "Operation",
    "control": "SelectEdit",
    "controlProps": {
      "object": "processOperation",
      "method": "getItemList",
      "valueField": "id",
      "displayField": "name_combined",
      "filterField": "type_code",
      "filterValue$": "mem.type_code"
    }
  }
}
```

## Reference Object Features

Each reference object provides:

1. **getItemList** method - loads all records from the database
2. **Reference form** with:
   - Multi-column display
   - Key field and title field configuration
   - Built-in filter panel
   - filterMethod for parametric filtering

3. **Filter capabilities**:
   - processType: filter by code or name
   - processState: filter by type_code (SelectEdit), code, or name
   - processOperation: filter by type_code (SelectEdit), code, or name

## Technical Details

- All references use `database='default'`
- processState and processOperation use UUID primary keys
- processOperation uses LEFT JOIN with process_operation_states to show aggregated state codes
- Filters use LIKE with UPPER() for case-insensitive search
- SelectEdit controls support cascading filters (type → state/operation)

## Data Model

```
process_type (code PK)
    ↓ FK: type_code
process_state (id PK, type_code+code UNIQUE)

process_type (code PK)
    ↓ FK: type_code
process_operation (id PK, type_code+code UNIQUE)
    ↓ FK: operation_id
process_operation_states (operation_id+state_code PK)
```

## Initial Data

After running `db_schema_process.sql`, you will have:
- 5 document types (from ref_message_types):
  - pacs.008 - Customer Credit Transfer
  - pacs.009 - Financial Institution Credit Transfer (COV)
  - camt.053 - Bank to Customer Statement
  - camt.054 - Bank to Customer Debit/Credit Notification
  - camt.056 - FI to FI Payment Cancellation Request

- 0 states (to be configured)
- 0 operations (to be configured)

## See Also

- Database schema: `db_schema_process.sql`
- Main documentation: SWIFT Process Management System
