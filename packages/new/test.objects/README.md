# Test Objects Package

Simple test package demonstrating basic CRUD operations.

## Objects

### simpleList

A basic list object with a single field `name` demonstrating:
- List view with columns
- Add/Edit/Delete operations
- Form validation
- In-memory storage (using Django cache)

## Structure

```
test.objects/
├── .configs/
│   ├── aoa.Object.xml          # Object configuration
│   └── workplace.Workplace.xml # Workplace configuration
├── ao/
│   └── simpleList.json         # Application Object definition
├── workplace/
│   └── test.manager.xml        # Workplace menu definition
├── .package.info               # Package metadata
└── README.md                   # This file
```

## Usage

1. Deploy package to system
2. Access via workplace: **Test Manager → Simple List**
3. Operations:
   - **Add**: Create new record with name
   - **Edit**: Double-click row or use Edit button
   - **Delete**: Select row and click Delete (with confirmation)
   - **Refresh**: Reload list

## Technical Details

- **Storage**: Django cache (in-memory, not persistent)
- **ID Generation**: UUID v4
- **Frontend**: FlexUI JSON forms
- **Backend**: Python methods

## Generated Using

This package was generated using AI-assisted code generation based on `SYSTEM_REFERENCE.md` patterns.

