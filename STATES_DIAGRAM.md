# Process States Diagram

## State Flow for SWIFT Documents

```
┌─────────────────────────────────────────────────────────────────┐
│                     SWIFT Message Received                       │
│                   (pacs.008, pacs.009, camt.*)                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   🟠 LOADED           │
                    │   (Загружен)          │
                    │                       │
                    │  Orange: #FF8C00      │
                    │  Edit: ✓ Yes          │
                    │  Delete: ✓ Yes        │
                    └───────────┬───────────┘
                                │
                                │ Document can be:
                                │ - Edited
                                │ - Deleted  
                                │ - Processed
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼ (ALL TYPES)                   ▼ (pacs.008 ONLY)
    ┌───────────────────────┐       ┌───────────────────────┐
    │  🔴 PROCESSED          │       │  🟢 PAYMENT_CREATED    │
    │  (Обработан)           │       │  (Платеж создан)       │
    │                        │       │                        │
    │  Burgundy: #8B0000     │       │  Green: #008000        │
    │  Edit: ✗ No            │       │  Edit: ✗ No            │
    │  Delete: ✗ No          │       │  Delete: ✗ No          │
    └────────────────────────┘       └────────────────────────┘
            │                                   │
            │                                   │
            └──────────► LOCKED ◄───────────────┘
                    (Cannot be modified)
```

## State Details

### 🟠 LOADED (Загружен)
**Initial state when document is imported**

- **Color**: Orange (#FF8C00 / DarkOrange)
- **Document Types**: ALL (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- **Permissions**:
  - ✓ Allow Edit
  - ✓ Allow Delete
- **Description**: Document has been successfully loaded into the system and is ready for processing

### 🔴 PROCESSED (Обработан)
**Document has been processed and locked**

- **Color**: Burgundy (#8B0000 / DarkRed)
- **Document Types**: ALL (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- **Permissions**:
  - ✗ No Edit
  - ✗ No Delete
- **Description**: Document has been processed by the system. No modifications allowed to ensure data integrity

### 🟢 PAYMENT_CREATED (Платеж создан)
**Payment document created in banking system**

- **Color**: Green (#008000)
- **Document Types**: ONLY pacs.008 (Customer Credit Transfer)
- **Permissions**:
  - ✗ No Edit
  - ✗ No Delete
- **Description**: Payment has been successfully created in the core banking system (АБС). Document is locked for audit purposes

## Document Type Coverage

| Document Type | Code | LOADED | PROCESSED | PAYMENT_CREATED |
|---------------|------|--------|-----------|-----------------|
| Customer Credit Transfer | pacs.008 | ✓ | ✓ | ✓ |
| FI Credit Transfer (COV) | pacs.009 | ✓ | ✓ | - |
| Bank to Customer Statement | camt.053 | ✓ | ✓ | - |
| Debit/Credit Notification | camt.054 | ✓ | ✓ | - |
| Cancel Payment | camt.056 | ✓ | ✓ | - |

## State Transitions

### Possible Transitions

```
LOADED → PROCESSED       (All document types)
LOADED → PAYMENT_CREATED (Only pacs.008)
```

### Locked States

Once a document enters `PROCESSED` or `PAYMENT_CREATED` state:
- ❌ Cannot be edited
- ❌ Cannot be deleted
- ❌ Cannot transition to other states
- ✓ Can only be viewed

## Color Codes Reference

```
🟠 #FF8C00  Orange     Document is active and editable
🔴 #8B0000  Burgundy   Document is processed and locked
🟢 #008000  Green      Payment created successfully
```

## Use Cases

### Standard Processing Flow
1. Message arrives → **LOADED** state (orange)
2. System validates and processes → **PROCESSED** state (burgundy)
3. Document is archived with full history

### Payment Creation Flow (pacs.008 only)
1. Payment message arrives → **LOADED** state (orange)
2. Payment created in banking system → **PAYMENT_CREATED** state (green)
3. Document is locked for audit trail

## Implementation Notes

- States are stored in `process_state` table
- Each state is linked to document type via `type_code`
- UI displays states with configured colors
- Workflow engine enforces edit/delete permissions
- State transitions are controlled by business logic

## Related Files

- `create_states_script.py` - Python script to create states
- `insert_states.sql` - SQL script to insert states
- `README_CREATE_STATES.md` - Detailed documentation
- `QUICKSTART_STATES.md` - Quick start guide
- `db_schema_process.sql` - Database schema

