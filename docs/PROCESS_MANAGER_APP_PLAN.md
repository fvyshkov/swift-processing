# Process Manager Web Application - Development Plan

## Overview

Standalone web application for managing process types, states, and operations using FastAPI backend and React frontend.

## Architecture

### Backend: FastAPI
- **Framework**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL (existing `process_*` tables)
- **ORM**: SQLAlchemy 2.0 with async support
- **API Style**: RESTful JSON API
- **Authentication**: JWT tokens (optional for v1, but recommended)

### Frontend: React
- **Framework**: React 18+ with TypeScript
- **State Management**: React Query (TanStack Query) + Zustand
- **UI Library**: Material-UI (MUI) v5
- **Routing**: React Router v6
- **Tree Component**: react-complex-tree or MUI TreeView
- **HTTP Client**: Axios

### Database Schema

Using existing tables:
- `process_type` - Process/document types (hierarchical)
- `process_state` - States for each type
- `process_operation` - Operations available for types
- `process_operation_states` - Many-to-many relation (operation available in which states)

## Application Structure

### Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Process Manager                              [Save Button]  │
├──────────┬────────────────────────────┬─────────────────────┤
│          │                            │                     │
│  LEFT    │        MIDDLE              │      RIGHT          │
│  PANEL   │        PANEL               │      PANEL          │
│          │                            │                     │
│  Tree    │  ┌──────────────────────┐  │  Attributes of      │
│  of      │  │ Type Attributes      │  │  selected item      │
│  Types   │  │ (editable)           │  │                     │
│          │  └──────────────────────┘  │  When State         │
│  📁 Type1│                            │  selected:          │
│  📁 Type2│  ┌──────────────────────┐  │  - state attrs      │
│    ├─S1  │  │ States List          │  │                     │
│    ├─S2  │  │ (colored rows)       │  │  When Operation     │
│    └─S3  │  │ + Add/Delete         │  │  selected:          │
│          │  └──────────────────────┘  │  - operation attrs  │
│          │                            │  - available states │
│          │  ┌──────────────────────┐  │                     │
│          │  │ Operations List      │  │  All editable       │
│          │  │ + Add/Delete         │  │  in-place           │
│          │  └──────────────────────┘  │                     │
│          │                            │                     │
└──────────┴────────────────────────────┴─────────────────────┘
```

### Left Panel: Type Navigator (Tree)
- Hierarchical tree view of process types
- Expandable/collapsible
- Click on type → shows type details in middle panel
- Visual indicators for type selection

### Middle Panel: Three Sections (stacked vertically)

#### Section 1: Type Attributes (editable)
- Code (read-only after creation)
- Name (English)
- Name (Russian)
- Combined Name
- Resource URL
- Attributes Table

#### Section 2: States List
- Grid/table with columns:
  - Code
  - Name (English/Russian/Combined)
  - Color (with color preview)
  - Allow Edit (checkbox)
  - Allow Delete (checkbox)
  - Start State (checkbox)
- Each row colored with `color_code` value
- Buttons: [+ Add State] [- Delete State]
- Clicking on row → selects state → right panel shows state attributes

#### Section 3: Operations List
- Grid/table with columns:
  - Code
  - Name (English/Russian/Combined)
  - Icon
  - Resource URL
  - Available in States (tags/chips)
- Buttons: [+ Add Operation] [- Delete Operation]
- Clicking on row → selects operation → right panel shows operation attributes

### Right Panel: Attributes Editor

#### When State is selected:
- **State ID** (read-only)
- **Type Code** (read-only)
- **Code** (editable, but read-only after creation)
- **Name (English)** (editable)
- **Name (Russian)** (editable)
- **Name (Combined)** (editable)
- **Color Code** (color picker)
- **Allow Edit** (checkbox)
- **Allow Delete** (checkbox)
- **Start State** (checkbox)

#### When Operation is selected:
- **Operation ID** (read-only)
- **Type Code** (read-only)
- **Code** (editable, but read-only after creation)
- **Name (English)** (editable)
- **Name (Russian)** (editable)
- **Name (Combined)** (editable)
- **Icon** (icon picker or text)
- **Resource URL** (textarea)
- **Database** (text field)
- **Workflow** (text field)
- **Move to State Script** (code editor, Python)
- **Availability Condition** (JSON editor)
- **Available in States** (multi-select checkboxes showing all states for this type)
- **Cancel** (checkbox)

### Navigation Flow

1. User selects Type in left panel
   - Middle panel shows Type attributes + States + Operations for this type
   - Right panel is empty (or shows type info)

2. User clicks on State row in middle panel
   - State row is highlighted
   - Right panel shows State attributes (editable)

3. User clicks on Operation row in middle panel
   - Operation row is highlighted
   - Right panel shows Operation attributes (editable)

4. User can switch between Type/State/Operation at any time
   - All changes are tracked in memory

5. User clicks **[Save]** button (top right)
   - All changes (Type + States + Operations) are sent to backend in one batch
   - Backend validates and saves everything in transaction
   - Success → show notification, refresh data
   - Error → show error details

## Backend API Endpoints

### Base URL: `/api/v1`

### Process Types

```
GET    /types                    - List all types (for tree)
GET    /types/{code}             - Get single type details
POST   /types                    - Create new type
PUT    /types/{code}             - Update type
DELETE /types/{code}             - Delete type
```

### Process States

```
GET    /types/{type_code}/states           - List states for type
GET    /states/{id}                        - Get single state
POST   /types/{type_code}/states           - Create state
PUT    /states/{id}                        - Update state
DELETE /states/{id}                        - Delete state
```

### Process Operations

```
GET    /types/{type_code}/operations       - List operations for type
GET    /operations/{id}                    - Get single operation
POST   /types/{type_code}/operations       - Create operation
PUT    /operations/{id}                    - Update operation
DELETE /operations/{id}                    - Delete operation
```

### Batch Save (Main Feature)

```
POST   /save-all                           - Save all pending changes
```

Request body:
```json
{
  "type": {
    "code": "pacs.008",
    "name_en": "...",
    "name_ru": "...",
    "name_combined": "...",
    "resource_url": "...",
    "attributes_table": "..."
  },
  "states": {
    "created": [...],
    "updated": [...],
    "deleted": [id1, id2, ...]
  },
  "operations": {
    "created": [...],
    "updated": [...],
    "deleted": [id1, id2, ...]
  },
  "operation_states": {
    "operation_id": [state_id1, state_id2, ...]
  }
}
```

## Frontend Components Structure

```
src/
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx          - Main 3-panel layout
│   │   ├── Header.tsx             - Top bar with Save button
│   │   └── Notifications.tsx      - Toast notifications
│   │
│   ├── navigation/
│   │   ├── TypeTree.tsx           - Left panel tree
│   │   └── TypeTreeNode.tsx       - Tree node component
│   │
│   ├── middle-panel/
│   │   ├── MiddlePanel.tsx        - Container for 3 sections
│   │   ├── TypeAttributesSection.tsx
│   │   ├── StatesListSection.tsx
│   │   └── OperationsListSection.tsx
│   │
│   ├── right-panel/
│   │   ├── RightPanel.tsx         - Container
│   │   ├── StateEditor.tsx        - State attributes editor
│   │   └── OperationEditor.tsx    - Operation attributes editor
│   │
│   └── common/
│       ├── ColorPicker.tsx
│       ├── CodeEditor.tsx         - For Python/JSON editing
│       ├── IconPicker.tsx
│       └── StateChip.tsx          - Colored chip for states
│
├── hooks/
│   ├── useTypes.ts                - React Query hooks for types
│   ├── useStates.ts               - React Query hooks for states
│   ├── useOperations.ts           - React Query hooks for operations
│   └── useChangeTracker.ts        - Track all changes before save
│
├── store/
│   ├── selectionStore.ts          - Zustand store for current selection
│   └── changesStore.ts            - Zustand store for pending changes
│
├── api/
│   ├── client.ts                  - Axios instance
│   ├── types.ts                   - API for types
│   ├── states.ts                  - API for states
│   └── operations.ts              - API for operations
│
├── types/
│   └── index.ts                   - TypeScript interfaces
│
└── App.tsx
```

## Data Flow

### 1. Initial Load
```
User opens app
  → Fetch all types (GET /types)
  → Display in left panel tree
  → No selection initially
```

### 2. Type Selection
```
User clicks Type in tree
  → Update selectionStore.selectedType
  → Fetch type details (GET /types/{code})
  → Fetch states (GET /types/{code}/states)
  → Fetch operations (GET /types/{code}/operations)
  → Display in middle panel
  → Clear right panel
```

### 3. State Selection
```
User clicks State row
  → Update selectionStore.selectedState
  → Display state attributes in right panel (editable)
  → Highlight state row
```

### 4. Editing State
```
User changes state attribute
  → Update changesStore (track change)
  → Update UI immediately (optimistic)
  → No API call yet
```

### 5. Operation Selection
```
User clicks Operation row
  → Update selectionStore.selectedOperation
  → Display operation attributes in right panel (editable)
  → Highlight operation row
  → Load available states for multi-select
```

### 6. Editing Operation
```
User changes operation attribute
  → Update changesStore (track change)
  → Update UI immediately (optimistic)
  → No API call yet
```

### 7. Add New State
```
User clicks [+ Add State]
  → Create new state object (with temp ID)
  → Add to changesStore.states.created
  → Add row to states list (highlighted as new)
  → Auto-select new state
  → Show in right panel for editing
```

### 8. Delete State
```
User clicks [- Delete State] for selected row
  → Confirm dialog
  → If new state → remove from created list
  → If existing → add to changesStore.states.deleted
  → Remove from UI
```

### 9. Save All
```
User clicks [Save] button
  → Collect all changes from changesStore
  → Build request body
  → POST /save-all
  → Backend processes in transaction:
      - Validate all changes
      - Update/Create/Delete in order
      - Return updated data
  → On success:
      - Clear changesStore
      - Refresh data from backend
      - Show success notification
  → On error:
      - Rollback (backend)
      - Show error notification
      - Keep changes in changesStore
```

## State Management

### Selection Store (Zustand)
```typescript
interface SelectionStore {
  selectedTypeCode: string | null;
  selectedStateId: string | null;
  selectedOperationId: string | null;
  
  selectType: (code: string) => void;
  selectState: (id: string) => void;
  selectOperation: (id: string) => void;
  clearSelection: () => void;
}
```

### Changes Store (Zustand)
```typescript
interface ChangesStore {
  hasChanges: boolean;
  
  type: TypeChanges | null;
  states: {
    created: State[];
    updated: State[];
    deleted: string[];
  };
  operations: {
    created: Operation[];
    updated: Operation[];
    deleted: string[];
  };
  
  updateType: (type: Type) => void;
  createState: (state: State) => void;
  updateState: (state: State) => void;
  deleteState: (id: string) => void;
  createOperation: (op: Operation) => void;
  updateOperation: (op: Operation) => void;
  deleteOperation: (id: string) => void;
  
  clear: () => void;
  buildSaveRequest: () => SaveAllRequest;
}
```

## TypeScript Interfaces

```typescript
interface ProcessType {
  code: string;
  name_en: string;
  name_ru: string;
  name_combined: string;
  resource_url?: string;
  attributes_table?: string;
}

interface ProcessState {
  id: string; // UUID
  type_code: string;
  code: string;
  name_en: string;
  name_ru: string;
  name_combined: string;
  color_code?: string; // hex color
  allow_edit: boolean;
  allow_delete: boolean;
  start: boolean;
}

interface ProcessOperation {
  id: string; // UUID
  type_code: string;
  code: string;
  name_en: string;
  name_ru: string;
  name_combined?: string;
  icon?: string;
  resource_url?: string;
  availability_condition?: string; // JSON
  cancel: boolean;
  to_state?: string;
  move_to_state_script?: string; // Python code
  workflow?: string;
  database?: string;
  available_states?: string[]; // state IDs
}

interface SaveAllRequest {
  type?: ProcessType;
  states: {
    created: ProcessState[];
    updated: ProcessState[];
    deleted: string[];
  };
  operations: {
    created: ProcessOperation[];
    updated: ProcessOperation[];
    deleted: string[];
  };
  operation_states: {
    [operation_id: string]: string[]; // state IDs
  };
}
```

## Backend Implementation

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    - FastAPI app entry point
│   ├── config.py                  - Configuration (DB connection, etc.)
│   ├── database.py                - Database session management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── process_type.py
│   │   ├── process_state.py
│   │   └── process_operation.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── process_type.py        - Pydantic schemas
│   │   ├── process_state.py
│   │   ├── process_operation.py
│   │   └── save_all.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                - Dependencies (DB session)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── types.py           - Type endpoints
│   │       ├── states.py          - State endpoints
│   │       ├── operations.py      - Operation endpoints
│   │       └── save_all.py        - Batch save endpoint
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── process_type.py        - CRUD operations
│   │   ├── process_state.py
│   │   └── process_operation.py
│   │
│   └── core/
│       ├── __init__.py
│       └── exceptions.py          - Custom exceptions
│
├── alembic/                       - Database migrations (optional)
├── tests/
├── requirements.txt
└── .env                           - Environment variables
```

### Key Files

#### `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import types, states, operations, save_all

app = FastAPI(title="Process Manager API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(types.router, prefix="/api/v1", tags=["types"])
app.include_router(states.router, prefix="/api/v1", tags=["states"])
app.include_router(operations.router, prefix="/api/v1", tags=["operations"])
app.include_router(save_all.router, prefix="/api/v1", tags=["save-all"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

#### `app/database.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
```

#### `app/api/v1/save_all.py` (Most Important)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.save_all import SaveAllRequest, SaveAllResponse
from app.crud import process_type, process_state, process_operation
from app.core.exceptions import ValidationError

router = APIRouter()

@router.post("/save-all", response_model=SaveAllResponse)
async def save_all_changes(
    request: SaveAllRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Save all pending changes in one transaction.
    Validates and applies all changes atomically.
    """
    async with db.begin():
        # 1. Update/Create Type
        if request.type:
            await process_type.upsert(db, request.type)
        
        # 2. Delete States
        for state_id in request.states.deleted:
            await process_state.delete(db, state_id)
        
        # 3. Create States
        for state in request.states.created:
            await process_state.create(db, state)
        
        # 4. Update States
        for state in request.states.updated:
            await process_state.update(db, state)
        
        # 5. Delete Operations
        for op_id in request.operations.deleted:
            await process_operation.delete(db, op_id)
        
        # 6. Create Operations
        for op in request.operations.created:
            await process_operation.create(db, op)
        
        # 7. Update Operations
        for op in request.operations.updated:
            await process_operation.update(db, op)
        
        # 8. Update Operation-States relations
        for op_id, state_ids in request.operation_states.items():
            await process_operation.update_states(db, op_id, state_ids)
    
    return {"success": True, "message": "All changes saved successfully"}
```

## Frontend Implementation

### Key Components

#### `components/layout/AppLayout.tsx`
```tsx
import React from 'react';
import { Box, Button } from '@mui/material';
import TypeTree from '../navigation/TypeTree';
import MiddlePanel from '../middle-panel/MiddlePanel';
import RightPanel from '../right-panel/RightPanel';
import { useChangesStore } from '../../store/changesStore';
import { useSaveAll } from '../../hooks/useSaveAll';

export default function AppLayout() {
  const hasChanges = useChangesStore(state => state.hasChanges);
  const { mutate: saveAll, isLoading } = useSaveAll();
  
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <h1>Process Manager</h1>
          <Button
            variant="contained"
            color="primary"
            disabled={!hasChanges || isLoading}
            onClick={() => saveAll()}
          >
            {isLoading ? 'Saving...' : 'Save All Changes'}
          </Button>
        </Box>
      </Box>
      
      {/* 3-panel layout */}
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Panel - 20% */}
        <Box sx={{ width: '20%', borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          <TypeTree />
        </Box>
        
        {/* Middle Panel - 50% */}
        <Box sx={{ width: '50%', borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
          <MiddlePanel />
        </Box>
        
        {/* Right Panel - 30% */}
        <Box sx={{ width: '30%', overflow: 'auto' }}>
          <RightPanel />
        </Box>
      </Box>
    </Box>
  );
}
```

## Development Phases

### Phase 1: Setup & Infrastructure (Week 1)
- [ ] Setup FastAPI project structure
- [ ] Setup React + TypeScript project (Vite or CRA)
- [ ] Configure PostgreSQL connection
- [ ] Create SQLAlchemy models matching existing DB schema
- [ ] Setup CORS and basic API routes
- [ ] Setup React Router and basic layout

### Phase 2: Backend Core (Week 1-2)
- [ ] Implement CRUD for Types
- [ ] Implement CRUD for States
- [ ] Implement CRUD for Operations
- [ ] Implement Operation-States relationship management
- [ ] Implement `/save-all` endpoint with transaction support
- [ ] Add validation and error handling
- [ ] Write API tests

### Phase 3: Frontend Core (Week 2-3)
- [ ] Setup React Query and Zustand stores
- [ ] Implement TypeTree component (left panel)
- [ ] Implement Type selection and data fetching
- [ ] Build MiddlePanel layout (3 sections)
- [ ] Implement TypeAttributesSection (editable)
- [ ] Implement StatesListSection (grid with colors)
- [ ] Implement OperationsListSection (grid)

### Phase 4: Editors & Change Tracking (Week 3-4)
- [ ] Build StateEditor component (right panel)
- [ ] Build OperationEditor component (right panel)
- [ ] Implement ColorPicker component
- [ ] Implement CodeEditor for Python/JSON
- [ ] Implement change tracking in Zustand store
- [ ] Add visual indicators for unsaved changes
- [ ] Implement [Save All] button logic

### Phase 5: Advanced Features (Week 4-5)
- [ ] Add/Delete States functionality
- [ ] Add/Delete Operations functionality
- [ ] Multi-select for Operation available states
- [ ] Icon picker for operations
- [ ] Validation on frontend before save
- [ ] Confirmation dialogs for destructive actions
- [ ] Loading states and error handling
- [ ] Toast notifications

### Phase 6: Polish & Testing (Week 5-6)
- [ ] Responsive design adjustments
- [ ] Keyboard shortcuts (Ctrl+S to save)
- [ ] Undo/Redo changes (optional)
- [ ] Dark mode support (optional)
- [ ] Performance optimization
- [ ] E2E tests with Playwright
- [ ] User documentation
- [ ] Deployment setup (Docker)

## Deployment

### Docker Setup

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/swift_processing
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: swift_processing
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./DB_CREATE_FULL.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  postgres_data:
```

## Security Considerations

### Authentication (Future)
- JWT tokens for API access
- Role-based access control (admin vs. viewer)
- Audit log for all changes

### Validation
- Backend validates all changes before committing
- Frontend prevents invalid states (e.g., duplicate codes)
- SQL injection prevention (SQLAlchemy ORM)

### CORS
- Whitelist only frontend domain in production
- Use environment variables for allowed origins

## Performance Optimization

### Backend
- Use async SQLAlchemy for concurrent operations
- Index on frequently queried fields (already in DB)
- Connection pooling
- Cache frequently accessed data (Redis optional)

### Frontend
- React.memo for expensive components
- Virtualization for long lists (react-window)
- Debounce search/filter inputs
- Code splitting by route

## Testing Strategy

### Backend Tests
- Unit tests for CRUD operations
- Integration tests for `/save-all` endpoint
- Transaction rollback tests
- Validation tests

### Frontend Tests
- Component tests (React Testing Library)
- Store tests (Zustand)
- API integration tests (MSW)
- E2E tests (Playwright)

## Monitoring & Logging

### Backend
- FastAPI request/response logging
- Database query logging (slow queries)
- Error tracking (Sentry optional)

### Frontend
- Console error tracking
- User action analytics (optional)
- Performance monitoring (Web Vitals)

## Future Enhancements

1. **Drag & Drop**: Reorder states/operations
2. **Bulk Import/Export**: JSON/CSV import/export
3. **Version History**: Track changes over time
4. **Visual Workflow Designer**: Draw state transitions
5. **Real-time Collaboration**: Multiple users editing
6. **Search & Filter**: Advanced filtering in lists
7. **Templates**: Pre-defined process type templates
8. **Workflow Simulation**: Test workflows before deployment

## Conclusion

This plan provides a comprehensive roadmap for building a standalone Process Manager web application. The architecture is designed to be scalable, maintainable, and user-friendly, with clear separation of concerns between backend and frontend.

**Estimated Timeline**: 5-6 weeks for MVP with core features.

**Team Requirements**:
- 1 Backend Developer (Python/FastAPI)
- 1 Frontend Developer (React/TypeScript)
- 1 Full-stack Developer (can work on both)

**Next Steps**:
1. Review and approve this plan
2. Setup development environment
3. Initialize Git repositories (monorepo or separate repos)
4. Begin Phase 1 implementation

