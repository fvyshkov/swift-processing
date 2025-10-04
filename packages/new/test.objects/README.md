# Test Objects Package

## Description

This package provides a simple list management functionality with basic CRUD operations using SQL-based storage.

## Prerequisites

**IMPORTANT**: Before installing this package, you must create the database objects (PostgreSQL):

```sql
create extension if not exists "pgcrypto";

create table if not exists simple_list (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    created_at timestamp without time zone not null default now()
);
```

The same DDL is stored inside the object under `methods.DATABASE_UPDATE.sql`.

## Features

- **Simple List**: A basic list with name field
  - Create new records (INSERT with RETURNING id)
  - Edit existing records (UPDATE)
  - Delete records (DELETE)
  - List all records (SELECT with ORDER BY)

## Installation

1. **Create the database table** (see Prerequisites above)

2. Archive the package:
   ```bash
   cd packages/new/test.objects
   zip -r ../test.objects.zip ao/ workplace/ .package.info README.md
   ```

3. Upload the `test.objects.zip` file through the package manager interface

## Structure

```
test.objects/
├── ao/
│   └── simpleList.json       # Object definition with forms and methods (contains DATABASE_UPDATE DDL)
├── workplace/
│   └── test.manager.xml      # Menu integration
├── .package.info             # Package metadata
└── README.md                 # This file
```

## Object Details

### simpleList

**Lists:**
- `default`: Main list showing all records with ID and Name columns (sorted by ID DESC)

**Forms:**
- `editForm`: Form for creating/editing records
  - Uses `mem.record` object pattern (like user.json)
  - Automatic TextEdit binding to `mem.record.name`
  - Save button enabled when name is filled

**Methods:**
- `getList`: SQL SELECT all records from simple_list table
- `get`: SQL SELECT single record by ID
- `save`: SQL INSERT (with RETURNING id) or UPDATE based on isNew flag
- `delete`: SQL DELETE by ID
- `DATABASE_UPDATE`: Non-executable DDL block storing table creation SQL

## Technical Details

All methods follow the pattern from existing objects:
- Using `initDbSession(database='default').cursor()`
- Using `fetchall()` and `fetchone()` from `apng_core.db`
- Parameterized queries with `%(param)s` syntax
- Proper error handling with `UserException`

## Testing

After installation, find "Simple List" in the Test menu to start using the functionality.
