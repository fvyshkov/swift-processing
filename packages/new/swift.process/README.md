# SWIFT Process Management Package

## Description

This package provides a comprehensive document state management system for SWIFT ISO 20022 message processing. It includes reference tables for document types, states, and operations, enabling flexible workflow configuration and tracking.

## Prerequisites

**IMPORTANT**: Before installing this package, you must create the database objects using the provided SQL schema:

Execute the file: `db_schema_process.sql`

This creates four tables:
- `process_type` - Document types reference
- `process_state` - Document states with colors and permissions
- `process_operation` - Available operations for documents
- `process_operation_states` - Many-to-many relation between operations and states

The schema also pre-populates `process_type` with data from `ref_message_types` table (5 SWIFT message types: pacs.008, pacs.009, camt.053, camt.054, camt.056).

## Features

### Process Management

Three integrated management interfaces in one application object:

#### 1. Document Types
- Manage document type definitions
- Define resource URLs for document display
- Pre-loaded with SWIFT ISO 20022 message types

#### 2. Document States
- Define states for each document type
- Assign color codes for UI display
- Configure edit/delete permissions per state
- Filter states by document type

#### 3. Document Operations
- Define available operations for document types
- Assign icons for UI representation
- Link operations to resource URLs (BPMN workflows, API endpoints)
- Configure availability conditions (JSON format)
- Associate operations with multiple states

## Architecture

The system follows the T_PROCINH pattern from Colvir for document relationships:
- Generic document linking without physical database FKs
- Support for cross-system document references (Colvir, external systems)
- Document journal with operation history
- Flexible state machine implementation

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
   cd packages/new/swift.process
   zip -r ../swift.process.zip ao/ workplace/ .configs/ .package.info README.md
   ```

4. **Upload** the `swift.process.zip` file through the package manager interface

## Structure

```
swift.process/
├── ao/
│   └── processManagement.json   # Complete application object
├── workplace/
│   └── process.manager.xml      # Menu with 3 sections
├── .configs/
│   ├── aoa.Object.xml           # Object registration
│   └── workplace.Workplace.xml  # Workplace registration
├── .package.info                # Package metadata
└── README.md                    # This file
```

## Object Details

### processManagement

**Lists:**
- `typeList`: Document types management
  - Columns: code, name_combined, resource_url
  - Actions: Add, Edit, Delete

- `stateList`: States management with filtering
  - Columns: type_code, code, name_combined, color (chip), allow_edit, allow_delete (checkboxes)
  - Filter by document type
  - Actions: Add, Edit, Delete

- `operationList`: Operations management with filtering
  - Columns: type_code, code, name_combined, icon, resource_url
  - Filter by document type
  - Actions: Add, Edit, Delete

**Forms:**
- `editType`: Edit document type
  - Fields: code (read-only after creation), names (en/ru/combined), resource_url

- `editState`: Edit document state
  - Fields: type_code, code (read-only after creation), names, color_code, allow_edit, allow_delete flags

- `editOperation`: Edit operation
  - Fields: type_code, code (read-only after creation), names, icon, resource_url, availability_condition (JSON)
  - state_codes: Multi-line text area for state associations

**Methods:**

Type Management:
- `getTypeList`: SELECT all types
- `getType`: SELECT single type by code
- `saveType`: INSERT/UPDATE type (UPSERT)
- `deleteType`: DELETE type (cascades to states and operations)

State Management:
- `getStateList`: SELECT all states with filtering support
- `getState`: SELECT single state by composite key
- `saveState`: INSERT/UPDATE state (UPSERT)
- `deleteState`: DELETE state

Operation Management:
- `getOperationList`: SELECT all operations with filtering support
- `getOperation`: SELECT operation with related states (JOIN)
- `saveOperation`: INSERT/UPDATE operation + manage state associations
- `deleteOperation`: DELETE operation (cascades to state associations)

## Usage Examples

### 1. Define a Document Type
```
Code: pacs.008
Name: Customer Credit Transfer
Resource URL: /aoa/ObjectTask?object=swiftInput&form=editForm&objectKey={id}
```

### 2. Define States for Type
```
Type: pacs.008
States:
  - NEW (color: #2196F3, allow_edit: true, allow_delete: true)
  - VALIDATED (color: #4CAF50, allow_edit: false, allow_delete: false)
  - SENT (color: #FF9800, allow_edit: false, allow_delete: false)
  - ERROR (color: #F44336, allow_edit: true, allow_delete: true)
```

### 3. Define Operations
```
Type: pacs.008
Code: validate
Name: Validate Payment
Icon: check_circle
Resource URL: /api/bpmn/validate-payment
Available in States:
  NEW
  ERROR
```

## Integration

The system is designed to integrate with:
- **BPMN Workflows**: Operations can trigger workflow execution
- **Document Tables**: Link to actual documents via type_code + document_key
- **Journal System**: Track operation execution history
- **External Systems**: Reference documents in Colvir or other systems using resource URLs

## Technical Details

- PostgreSQL database with proper FK constraints and indexes
- UUID for operation IDs (cross-system compatibility)
- Composite keys for states (type_code + code)
- ON CONFLICT DO UPDATE for all save operations
- CASCADE DELETE for referential integrity
- Filter support using `apng_core.aoa.services.filter`
- Parameterized queries with proper SQL injection protection

## Future Extensions

This system provides the foundation for:
- Document action history (journal table)
- Document relationships (T_PROCINH analog)
- State transition validation
- Operation availability checking
- Workflow integration
- Cross-system document linking

## Testing

After installation:
1. Navigate to "Process Manager" workplace
2. Open "Document Types" - verify 5 SWIFT types are loaded
3. Create states for a document type
4. Create operations and associate with states
5. Verify filtering works correctly
