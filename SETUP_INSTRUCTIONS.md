# Process Manager Setup Instructions

## Status

✅ Backend structure created
✅ Frontend structure created  
✅ Backend dependencies installed
⚠️ PostgreSQL database needs to be started
⚠️ Frontend dependencies need to be installed (Node.js required)

## What's Been Created

### Backend (FastAPI)
- Complete REST API with endpoints for types, states, operations
- SQLAlchemy models matching your database schema
- Pydantic schemas for validation
- CRUD operations
- Save-all endpoint for batch updates

### Frontend (React + TypeScript)
- 3-panel layout (Type Tree | Details | Editor)
- Material-UI components
- React Query for data fetching
- Zustand for state management
- Full TypeScript support

## Next Steps

### 1. Start PostgreSQL

You need PostgreSQL running with your database. Options:

**Option A: Start Docker (if Docker Desktop is installed)**
```bash
# Start Docker Desktop app first, then:
docker-compose up -d
```

**Option B: Use local PostgreSQL**
```bash
# If you have PostgreSQL installed via Homebrew:
brew services start postgresql@15

# Create database and load data:
createdb swift_processing
psql swift_processing < process.txt
```

**Option C: Install PostgreSQL**
```bash
# Install via Homebrew:
brew install postgresql@15
brew services start postgresql@15

# Then create database:
createdb swift_processing
psql swift_processing < process.txt
```

### 2. Start Backend

```bash
# Simple way:
./start_backend.sh

# Or manually:
export PATH="/Users/fvyshkov/Library/Python/3.9/bin:$PATH"
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: http://localhost:8000
API docs will be at: http://localhost:8000/docs

### 3. Install Node.js and Frontend Dependencies

```bash
# Install Node.js via Homebrew:
brew install node

# Then install frontend dependencies:
cd frontend
npm install

# Start frontend:
npm run dev
```

Frontend will be at: http://localhost:3000

## Verify Everything Works

1. **Database**: Run `psql swift_processing -c "SELECT COUNT(*) FROM process_type;"`
   - Should return count of process types

2. **Backend**: Open http://localhost:8000/health
   - Should return `{"status": "ok"}`

3. **Frontend**: Open http://localhost:3000
   - Should show Process Manager interface

## Database Schema

The application uses your existing tables from `process.txt`:
- `process_type` (7 records) - Process types with hierarchy
- `process_state` (13 records) - States for each type
- `process_operation` (14 records) - Operations for types
- `process_operation_states` (11 records) - Operation-state relationships

## Troubleshooting

### "Cannot connect to database"

Check PostgreSQL is running:
```bash
# Check if postgres is running
ps aux | grep postgres

# Check connection
psql swift_processing -c "SELECT version();"
```

If using Docker, make sure Docker Desktop is running.

### "Module not found" errors in backend

Make sure uvicorn is in PATH:
```bash
export PATH="/Users/fvyshkov/Library/Python/3.9/bin:$PATH"
```

Or use:
```bash
python3 -m uvicorn app.main:app --reload
```

### Frontend won't start

Install Node.js first:
```bash
brew install node
```

## What You Can Do

Once everything is running:

1. **Browse Types**: Click on types in the left panel (SWIFT, pacs.008, etc.)
2. **View States**: See states for each type with their colors
3. **View Operations**: See available operations
4. **Edit Details**: Click on a state or operation to edit in the right panel
5. **Save Changes**: (Note: Save functionality needs change tracking to be fully wired)

## Current Limitations

The following are implemented but may need testing:
- ✅ Basic CRUD operations
- ✅ Data loading and display
- ✅ Three-panel layout
- ⚠️ Change tracking (basic structure in place, needs testing)
- ⚠️ Save all changes (endpoint exists, needs frontend wiring)
- ❌ Add/Delete states and operations (UI buttons not added yet)
- ❌ Hierarchical tree view (showing flat list currently)
- ❌ Color picker for states
- ❌ Code editor for Python scripts

## Files Created

### Backend
- `backend/app/main.py` - FastAPI application
- `backend/app/database.py` - Database configuration
- `backend/app/models/` - SQLAlchemy models
- `backend/app/schemas/` - Pydantic schemas
- `backend/app/crud/` - CRUD operations
- `backend/app/api/v1/` - API endpoints

### Frontend
- `frontend/src/App.tsx` - Main application
- `frontend/src/components/layout/AppLayout.tsx` - 3-panel layout
- `frontend/src/components/navigation/TypeTree.tsx` - Left panel
- `frontend/src/components/middle-panel/` - Middle panel components
- `frontend/src/components/right-panel/` - Right panel editors
- `frontend/src/store/` - Zustand stores
- `frontend/src/hooks/` - React Query hooks
- `frontend/src/api/` - API client

## Database Connection String

Default: `postgresql+asyncpg://postgres:postgres@localhost:5432/swift_processing`

Change in `backend/.env` if needed.

