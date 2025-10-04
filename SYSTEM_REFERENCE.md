# System Architecture Reference

> **Purpose**: This document serves as a context reference for AI-assisted generation of new objects, forms, and business logic implementations. Not intended for human reading - optimized for LLM context.

---

## 1. PACKAGE STRUCTURE

```
packages/
├── current/          # Production instance
│   ├── core/
│   │   ├── ao/            # Application Objects (JSON)
│   │   ├── configuration/ # Object configs (XML)
│   │   ├── users/         # User definitions (XML)
│   │   └── workplace/     # Workplace definitions (XML/JSON)
│   └── easyflow/
└── new/              # Development instance (ISOLATED from current)
    ├── bank.app_settings/
    ├── bank.core_objects/
    ├── bank.uz_app/
    ├── bank.uz_core/
    └── core/
```

**CRITICAL**: `current` and `new` are separate instances with NO cross-references.

---

## 2. APPLICATION OBJECT STRUCTURE (AO)

### 2.1 Root Level Keys

```json
{
  "filter": {},        // List filter form + SQL queries
  "actions": [],       // Object-level actions (buttons/operations)
  "forms": {},         // Named form definitions
  "methods": {},       // Backend methods (Python/SQL)
  "lists": {},         // List view definitions
  "references": {},    // Lookup references
  "js": {}            // Client-side JavaScript
}
```

### 2.2 Filter Definition

```json
"filter": {
  "form": {
    "style": { "width": "360px" },
    "title": "Filter title",
    "className": "panel vertical",
    "$": {
      "@fields": {
        "$": {
          "fieldName": {
            "control": "TextEdit|SelectList|DateEdit|ModuleComponent",
            "label": "Field Label",
            "controlProps": {},
            "controlOpts": {}
          }
        }
      },
      "@buttons": {
        "btnApply": {
          "control": "Button",
          "action": { "js": "actions.apply(mem);" }
        }
      }
    },
    "actions": {
      "clean": { "jsScript": "Object.keys(mem).forEach(key => delete mem[key]);" }
    }
  },
  "query": {
    "fieldName": {
      "sql": "column_name = :fieldName"
    }
  }
}
```

**Pattern**: 
- Form fields in `$` section with `@` prefix for grouping
- SQL queries map field names to WHERE clauses
- Parameter binding uses `:paramName` notation

---

## 3. FORMS SYSTEM

### 3.1 Form Structure Pattern

```json
"forms": {
  "formName": {
    "title": "Form Title",
    "className": "vertical|horizontal task task-panel panel",
    "style": {},
    "$": {
      "@section": {
        "title": "Section Title",
        "className": "vertical",
        "$": {
          "fieldName": {
            "label": "Label",
            "control": "TextEdit|Button|SelectList|...",
            "controlProps": {},
            "controlOpts": {},
            "action": {},
            "readOnly": false,
            "visible$": "expression",
            "readOnly$": "expression"
          }
        }
      }
    },
    "actions": {
      "actionName": {
        "js": "javascript code",
        "jsScript": "javascript code",
        "name": "anotherAction"
      }
    }
  }
}
```

### 3.2 Naming Conventions

| Prefix | Purpose | Example |
|--------|---------|---------|
| `@` | Section/group | `@client`, `@buttons`, `@form` |
| `.` | Singleton element | `.btnSave`, `.error`, `.text` |
| `\|` | Array/list | `\|salaries`, `\|product_list` |
| none | Named field | `firstName`, `amount`, `pinfl` |

### 3.3 Control Types

```typescript
// Input controls
TextEdit          // Single line text
DateEdit          // Date picker
CurrencyField     // Formatted currency
PositiveIntegerField
SelectList        // Dropdown
Chip             // Chip button

// Complex controls
ModuleComponent   // Embedded component
ObjectReference   // Reference to another object
ActionPanel       // Button group
ListTable        // Data grid
Button           // Action button

// Display
Text             // Static text
```

### 3.4 Dynamic Expressions

```json
{
  "visible$": "user.groups.includes('ADMINS')",
  "readOnly$": "!mem.code || params.readOnly",
  "disabled$": "!$listRow",
  "title$": "`Application ${mem.appNo}`",
  "value$": "context.selectedValue"
}
```

**Pattern**: Fields ending with `$` contain JavaScript expressions evaluated at runtime.

---

## 4. METHODS SYSTEM

### 4.1 Method Structure

```json
"methods": {
  "methodName": {
    "sql": {
      "params": []
    },
    "script": {
      "params": [],
      "py": "Python code here"
    }
  }
}
```

### 4.2 Common Method Patterns

**Data retrieval:**
```python
from apng_core.db import fetchall, fetchone

with initDbSession(application='bank').cursor() as cursor:
    cursor.execute(SQL, params)
    data = fetchall(cursor)
```

**Transaction handling:**
```python
from django.db import transaction
from django.conf import settings

with transaction.atomic(using=settings.APPS_DB['bank']):
    # database operations
```

**Error handling:**
```python
from apng_core.exceptions import UserException

raise UserException({
    'message': 'Error description',
    'trace': log.readLog()
})
```

**Object method calls:**
```python
from apng_core.aoa.services import execObjectMethod

result = execObjectMethod({
    'object': 'objectName',
    'method': 'methodName',
    'params': {...}
})
```

---

## 5. LISTS SYSTEM

### 5.1 List Definition

```json
"lists": {
  "default": {
    "id": "primaryKeyField",
    "columns": {
      "columnName": {
        "title": "Column Title",
        "width": 160,
        "flex": 1,
        "fields": {
          "field1": { "format": "date|currency|datetime" },
          "field2": {}
        },
        "control": "chip",
        "decode": {
          "VALUE": { "value": "Display", "color": "#hex" }
        },
        "cellStyle": {}
      }
    },
    "actions": [],
    "filter": {},
    "events": {
      "onRowDoubleClicked": { "js": "..." },
      "onTaskCreated": []
    }
  }
}
```

### 5.2 Column Types

**Simple field:**
```json
"columnName": {
  "title": "Title",
  "width": 120
}
```

**Composite field:**
```json
"clientAndProduct": {
  "title": "Customer/Product",
  "fields": {
    "cli_name": {},
    "product_name": {}
  }
}
```

**Decoded field (Status):**
```json
"state": {
  "title": "State",
  "control": "chip",
  "decode": {
    "START": { "value": "Created", "color": "#2D9CDB" },
    "COMPLETED": { "value": "Completed", "color": "#00AA44" }
  }
}
```

---

## 6. ACTIONS SYSTEM

### 6.1 Action Definition

```json
{
  "name": "Action Name",
  "title": "Action Title",
  "icon": "view|edit|delete|refresh|add",
  "mini": true,
  "split": true,
  "command": {
    "type": "task|workflow|js|standard",
    "call": "/path/to/task",
    "params": {},
    "js": "javascript code"
  },
  "action": {
    "name": "actionName",
    "js": "javascript code",
    "params": {}
  },
  "confirm": {
    "message": "Confirmation text",
    "message$": "`Dynamic ${variable}`",
    "yes": "Yes",
    "no": "No"
  },
  "visible": "expression",
  "visible$": "dynamic expression",
  "disabled": "expression",
  "disabled$": "dynamic expression"
}
```

### 6.2 Command Types

**Task:**
```json
{
  "type": "task",
  "call": "/aoa/ObjectTask",
  "title$": "`Title ${variable}`",
  "params": {
    "object": "objectName",
    "form": "formName",
    "objectKey": { "dep_id": 123, "id": 456 }
  }
}
```

**Workflow:**
```json
{
  "type": "workflow",
  "call": "WORKFLOW_CODE",
  "params": {
    "objectKey$": "`loanapp:${dep_id},${id}`"
  }
}
```

**JavaScript:**
```json
{
  "type": "js",
  "js": "frontend.displayInfo(JSON.stringify($listRow));"
}
```

---

## 7. WORKPLACE STRUCTURE (XML)

```xml
<workplace code="workplace.code" name="Display Name">
  <menu name="Menu Name">
    <menu name="Submenu" call="/aoa/ObjectListTask">
      <p name="object" value="objectName" />
      <p name="list" value="listName" />
    </menu>
    <menu name="Task Menu" call="/aoa/ObjectTask">
      <p name="object" value="objectName" />
      <p name="form" value="formName" />
    </menu>
  </menu>
</workplace>
```

### 7.1 Standard Calls

- `/aoa/ObjectListTask` - Display object list
- `/aoa/ObjectTask` - Display object form/task
- `/aoa/ObjectTask` with template - Display report

---

## 8. STANDARD PATTERNS

### 8.1 Form Action Handlers

```json
"actions": {
  "onElementCreated": { "name": "onFormCreated" },
  "onFormCreated": {
    "js": "backend.post('/aoa/execObjectMethod', {...})"
  },
  "onChange": [
    { "js": "mem.field = value;" },
    { "name": "validateField" }
  ],
  "onSelectionChanged": {
    "js": "context.selected = selectedRow;"
  }
}
```

### 8.2 Dialog Pattern

```json
"dialogName": {
  "title": "Dialog Title",
  "style": { "width": "800px", "height": "600px" },
  "className": "vertical",
  "$": {
    "@form": { /* form fields */ },
    "@buttons": {
      "className": "horizontal",
      "$": {
        ".btnClose": {
          "action": { "js": "actions.close();" }
        },
        ".btnApply": {
          "action": [
            { "js": "/* validation */" },
            { "js": "actions.close();" }
          ]
        }
      }
    }
  }
}
```

### 8.3 List with Actions Pattern

```json
"|listField": {
  "$": {
    ".ap": {
      "control": "ActionPanel",
      "controlOpts": {
        "actions": [
          { "title": "Add", "icon": "add", "action": {} },
          { "title": "Delete", "icon": "delete", "action": {} }
        ]
      }
    },
    ".list": {
      "control": "ListTable",
      "controlOpts": { "$": { /* columns */ } }
    }
  },
  "actions": {
    "onSelectionChanged": {}
  }
}
```

### 8.4 Nested Object Pattern

```json
"@section": {
  "$": {
    "field": {
      "$": {
        "@control": {
          "object": "objectName",
          "form": "formName",
          "params": {}
        }
      }
    }
  }
}
```

---

## 9. SQL PATTERNS

### 9.1 Parameter Binding

```sql
-- Simple parameter
WHERE column = :paramName

-- Array parameter (JSON)
WHERE code IN (SELECT * FROM json_table(:list, '$.*' COLUMNS(value path '$')))

-- Date parameter
WHERE date_column >= to_date(:fromDate, 'yyyy-mm-dd')

-- Hierarchical query
WHERE code = any(
  SELECT code FROM table 
  START WITH code=:rootCode 
  CONNECT BY id_hi=PRIOR id
)
```

### 9.2 JSON Operations (Oracle)

```sql
-- Extract value
json_value(json_column, '$.path.to.value')

-- Query JSON array
json_query(json_column, '$.array[*]')

-- JSON table
FROM json_table(
  json_column, 
  '$.*' COLUMNS(
    field1 path '$.field1',
    field2 path '$.field2'
  )
)
```

---

## 10. JAVASCRIPT CONTEXT OBJECTS

### 10.1 Available Variables

```javascript
// Form context
mem          // Form memory/data
params       // Form parameters
context      // Shared context
validator    // Validation object
dialog       // Dialog actions

// List context
$listRow     // Selected list row
selectedRow  // Selected row
$formatters  // Formatting functions

// Global
user         // Current user object
backend      // Backend API
frontend     // Frontend API
task         // Task object
tm           // Task manager
```

### 10.2 Common Operations

```javascript
// Update form
forceUpdate();

// Backend call
backend.post('/aoa/execObjectMethod', {
  object: 'name',
  method: 'methodName',
  params: {}
}, { silent: true, useCache: true });

// Open dialog
frontend.dialog({
  object: 'objectName',
  form: 'formName',
  mem: {},
  params: {}
});

// Start workflow
frontend.easyflow.startProcessByCode('CODE', params, callback);

// Open task
tm.newTask({
  title: 'Task Title',
  path: '/aoa/ObjectTask',
  params: {}
});

// Close current task
frontend.closeTask();
```

---

## 11. VALIDATION PATTERNS

### 11.1 Field Validation

```javascript
// Set error
setError(validator.$.fieldName);

// Clear error
cleanErrors(validator.$.fieldName);

// Validate form
if (!dialog.actions.validate()) return;
```

### 11.2 ReadOnly Expressions

```json
"readOnly$": "!mem.newUser",
"readOnly$": "!params.isNew || !context.enabled",
"readOnly$": "isReadOnly || !user.superuser"
```

---

## 12. STYLING PATTERNS

### 12.1 Layout Classes

```
vertical          // Vertical flexbox
horizontal        // Horizontal flexbox
panel            // Panel styling
task             // Task styling
task-panel       // Combined
navigated-title  // Navigation title
navigated-content // Navigation content
```

### 12.2 Common Styles

```json
"style": {
  "width": "400px",
  "flexGrow": 1,
  "overflow": "hidden",
  "paddingRight": "8px",
  "marginTop": "4px"
}
```

---

## 13. INTERNATIONALIZATION

### 13.1 Translation Function

```javascript
// Direct translation
_('Text to translate')

// Template literal
`${_('Application')} ${code}`

// In JSON
"name$": "_('Customer')"
```

---

## 14. ERROR HANDLING PATTERNS

### 14.1 Python Exceptions

```python
# User-facing error
raise UserException('Error message')

# With trace
raise UserException({
    'message': 'Error description',
    'trace': log.readLog()
})

# With details
raise UserError({
    'message': 'User error message',
    'details': error_details
})
```

### 14.2 JavaScript Errors

```javascript
// Display error
frontend.displayError('Error message');

// Display info
frontend.displayInfo(JSON.stringify(data, null, 4));
```

---

## 15. GENERATION CHECKLIST

When creating new object:

- [ ] Define package location (new/ only)
- [ ] Create AO JSON with: filter, forms, methods, lists, actions
- [ ] Define workplace XML with menu structure
- [ ] Implement backend methods (Python)
- [ ] Define SQL queries for filters
- [ ] Create form actions and handlers
- [ ] Add list columns and formatting
- [ ] Define action buttons with permissions
- [ ] Add validation logic
- [ ] Implement error handling
- [ ] Add internationalization strings

---

## 16. CONVENTIONS

### 16.1 Naming

- Objects: `lowercase` or `namespace.object`
- Forms: `camelCaseTask` or `camelCaseForm` or `camelCaseDialog`
- Methods: `camelCase`
- Fields: `camelCase`
- SQL params: `UPPER_CASE` or `snake_case`

### 16.2 Comments

**Python**: English only
**JavaScript**: English only
**User-facing strings**: Localized with `_()`

### 16.3 State Management

- Use `mem` for form state
- Use `context` for cross-component state
- Use `params` for immutable inputs

---

**END OF REFERENCE**

*This document should be included in AI context when generating new objects, forms, or business logic.*

