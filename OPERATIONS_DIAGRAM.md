# Process Operations & State Transitions

## Complete State Transition Diagram

```
                     ┌─────────────────────────────────┐
                     │      🟠 LOADED (Загружен)        │
                     │                                 │
                     │  Orange: #FF8C00                │
                     │  Edit: ✓  Delete: ✓             │
                     └──┬────────────────────────────┬─┘
                        │                            │
         ┌──────────────┴──────────┐                 │
         │                         │                 │
    ALL TYPES                  pacs.008 ONLY         │
         │                         │                 │
         ▼                         ▼                 │
  ┌─────────────────┐    ┌──────────────────┐       │
  │ MARK_AS_        │    │ CREATE_PAYMENT   │       │
  │ PROCESSED       │    │                  │       │
  │ (check icon)    │    │ (payment icon)   │       │
  └────────┬────────┘    └────────┬─────────┘       │
           │                      │                 │
           ▼                      ▼                 │
  ┌──────────────────┐   ┌──────────────────┐      │
  │ 🔴 PROCESSED      │   │ 🟢 PAYMENT_      │      │
  │ (Обработан)       │   │    CREATED       │      │
  │                   │   │ (Платеж создан)  │      │
  │ Burgundy: #8B0000 │   │ Green: #008000   │      │
  │ Edit: ✗ Delete: ✗ │   │ Edit: ✗ Delete: ✗│      │
  └────────┬──────────┘   └────────┬─────────┘      │
           │                       │                │
           │ CANCEL_PROCESSING     │ CANCEL_PAYMENT │
           │ (undo icon)           │ (cancel icon)  │
           └───────────────────────┴────────────────┘
                                   │
                                   ▼
                         Back to LOADED state
```

## Operations Overview

### 1. ✓ MARK_AS_PROCESSED (Отметить как обработанный)

**Forward Operation: LOADED → PROCESSED**

- **Document Types**: ALL (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- **Icon**: `check` ✓
- **Available in States**: LOADED
- **Target State**: PROCESSED
- **Resource URL**: `/aoa/ProcessAction?action=markProcessed&docId={id}&docType={type}`
- **Use Case**: Mark document as processed after validation/review

**What it does:**
- Changes document state from LOADED to PROCESSED
- Locks document (no more editing/deletion allowed)
- Records processing timestamp
- Updates document audit trail

---

### 2. ↶ CANCEL_PROCESSING (Отменить обработку)

**Reverse Operation: PROCESSED → LOADED**

- **Document Types**: ALL (pacs.008, pacs.009, camt.053, camt.054, camt.056)
- **Icon**: `undo` ↶
- **Available in States**: PROCESSED
- **Target State**: LOADED
- **Resource URL**: `/aoa/ProcessAction?action=cancelProcessing&docId={id}&docType={type}`
- **Use Case**: Revert processed document back to editable state

**What it does:**
- Changes document state from PROCESSED back to LOADED
- Unlocks document (allows editing/deletion)
- Records cancellation reason
- Updates document audit trail

---

### 3. 💳 CREATE_PAYMENT (Создать платеж)

**Forward Operation: LOADED → PAYMENT_CREATED** *(pacs.008 only)*

- **Document Types**: ONLY pacs.008 (Customer Credit Transfer)
- **Icon**: `payment` 💳
- **Available in States**: LOADED
- **Target State**: PAYMENT_CREATED
- **Resource URL**: `/aoa/ProcessAction?action=createPayment&docId={id}&docType={type}`
- **Use Case**: Create payment in banking system based on pacs.008 message

**What it does:**
- Opens form to select Debit/Credit accounts
- Validates payment details
- Creates payment document in core banking system (АБС)
- Changes document state to PAYMENT_CREATED
- Records payment reference
- Locks document (no more editing/deletion)

---

### 4. ✕ CANCEL_PAYMENT (Отменить создание платежа)

**Reverse Operation: PAYMENT_CREATED → LOADED** *(pacs.008 only)*

- **Document Types**: ONLY pacs.008 (Customer Credit Transfer)
- **Icon**: `cancel` ✕
- **Available in States**: PAYMENT_CREATED
- **Target State**: LOADED
- **Resource URL**: `/aoa/ProcessAction?action=cancelPayment&docId={id}&docType={type}`
- **Use Case**: Cancel payment creation and revert to editable state

**What it does:**
- Validates that payment can be cancelled
- Cancels payment in core banking system (if applicable)
- Changes document state from PAYMENT_CREATED back to LOADED
- Unlocks document (allows editing/deletion)
- Records cancellation reason and timestamp

---

## Operations by Document Type

### pacs.008 (Customer Credit Transfer)
```
LOADED:
  → [✓] Mark as Processed → PROCESSED
  → [💳] Create Payment → PAYMENT_CREATED

PROCESSED:
  → [↶] Cancel Processing → LOADED

PAYMENT_CREATED:
  → [✕] Cancel Payment → LOADED
```

### pacs.009 (FI Credit Transfer)
```
LOADED:
  → [✓] Mark as Processed → PROCESSED

PROCESSED:
  → [↶] Cancel Processing → LOADED
```

### camt.053 (Bank Statement)
```
LOADED:
  → [✓] Mark as Processed → PROCESSED

PROCESSED:
  → [↶] Cancel Processing → LOADED
```

### camt.054 (Debit/Credit Notification)
```
LOADED:
  → [✓] Mark as Processed → PROCESSED

PROCESSED:
  → [↶] Cancel Processing → LOADED
```

### camt.056 (Cancel Payment)
```
LOADED:
  → [✓] Mark as Processed → PROCESSED

PROCESSED:
  → [↶] Cancel Processing → LOADED
```

---

## Operation Matrix

| Operation | pacs.008 | pacs.009 | camt.053 | camt.054 | camt.056 | From State | To State |
|-----------|----------|----------|----------|----------|----------|------------|----------|
| MARK_AS_PROCESSED | ✓ | ✓ | ✓ | ✓ | ✓ | LOADED | PROCESSED |
| CANCEL_PROCESSING | ✓ | ✓ | ✓ | ✓ | ✓ | PROCESSED | LOADED |
| CREATE_PAYMENT | ✓ | - | - | - | - | LOADED | PAYMENT_CREATED |
| CANCEL_PAYMENT | ✓ | - | - | - | - | PAYMENT_CREATED | LOADED |

**Total Operations Created**: 14
- 5 × MARK_AS_PROCESSED (one per document type)
- 5 × CANCEL_PROCESSING (one per document type)
- 1 × CREATE_PAYMENT (pacs.008 only)
- 1 × CANCEL_PAYMENT (pacs.008 only)
- 2 × Additional states reserved (PAYMENT_CREATED for pacs.008)

---

## State Locks & Permissions

### Unlocked State: 🟠 LOADED
- ✓ Can Edit
- ✓ Can Delete
- ✓ Operations Available: 2-3 (depending on type)

### Locked States: 🔴 PROCESSED & 🟢 PAYMENT_CREATED
- ✗ Cannot Edit
- ✗ Cannot Delete
- ✓ Operations Available: 1 (reverse operation only)

---

## Icon Reference

| Icon | Symbol | Meaning | Operations |
|------|--------|---------|------------|
| `check` | ✓ | Approve/Complete | MARK_AS_PROCESSED |
| `undo` | ↶ | Reverse/Cancel | CANCEL_PROCESSING |
| `payment` | 💳 | Create Payment | CREATE_PAYMENT |
| `cancel` | ✕ | Cancel Action | CANCEL_PAYMENT |

---

## Workflow Examples

### Example 1: Standard Processing (All Types)
```
1. Document arrives → LOADED (orange)
2. User clicks [✓ Mark as Processed]
3. Document → PROCESSED (burgundy, locked)
4. If needed: User clicks [↶ Cancel Processing]
5. Document → LOADED (orange, unlocked)
```

### Example 2: Payment Creation (pacs.008 only)
```
1. Payment message arrives → LOADED (orange)
2. User clicks [💳 Create Payment]
3. Form opens: Select Debit/Credit accounts
4. Payment created in АБС
5. Document → PAYMENT_CREATED (green, locked)
6. If needed: User clicks [✕ Cancel Payment]
7. Payment cancelled, Document → LOADED (orange, unlocked)
```

---

## Database Structure

### process_operation Table
```sql
CREATE TABLE process_operation (
    id uuid PRIMARY KEY,
    type_code text NOT NULL,           -- FK to process_type
    code text NOT NULL,                -- Operation code
    name_en text NOT NULL,
    name_ru text NOT NULL,
    name_combined text NOT NULL,
    icon text,                         -- Icon identifier
    resource_url text,                 -- URL to execute operation
    availability_condition text,       -- JSON: available states, target
    UNIQUE (type_code, code)
);
```

### process_operation_states Table (Many-to-Many)
```sql
CREATE TABLE process_operation_states (
    operation_id uuid NOT NULL,        -- FK to process_operation
    state_id uuid NOT NULL,            -- FK to process_state
    PRIMARY KEY (operation_id, state_id)
);
```

---

## Related Files

- `create_operations_script.py` - Python script to create operations
- `insert_operations.sql` - SQL script to insert operations
- `README_CREATE_OPERATIONS.md` - Detailed documentation
- `queries_operations.sql` - Useful SQL queries
- `STATES_DIAGRAM.md` - State reference diagram

