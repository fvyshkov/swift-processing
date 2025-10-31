# Process Manager Application

Web application for managing process types, states, and operations.

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Material-UI
- **Database**: PostgreSQL

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+ and npm

## Quick Start

### 1. Start PostgreSQL Database

```bash
docker-compose up -d
```

This will start PostgreSQL with the data from `process.txt`.

### 2. Setup Backend

```bash
cd backend

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Select a process type from the left panel
3. View and edit states and operations in the middle panel
4. Click on a state or operation to edit details in the right panel
5. Click "Save All Changes" to persist your changes

## Project Structure

### Backend (`/backend`)

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── crud/            # CRUD operations
│   ├── core/            # Core utilities
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI app
└── requirements.txt
```

### Frontend (`/frontend`)

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── layout/
│   │   ├── navigation/
│   │   ├── middle-panel/
│   │   └── right-panel/
│   ├── hooks/           # React Query hooks
│   ├── store/           # Zustand state management
│   ├── api/             # API client
│   ├── types/           # TypeScript types
│   ├── App.tsx
│   └── main.tsx
└── package.json
```

## API Endpoints

### Process Types
- `GET /api/v1/types` - Get all types
- `GET /api/v1/types/{code}` - Get type by code
- `POST /api/v1/types` - Create type
- `PUT /api/v1/types/{code}` - Update type

### Process States
- `GET /api/v1/types/{type_code}/states` - Get states for type
- `GET /api/v1/states/{id}` - Get state by ID
- `POST /api/v1/types/{type_code}/states` - Create state
- `PUT /api/v1/states/{id}` - Update state
- `DELETE /api/v1/states/{id}` - Delete state

### Process Operations
- `GET /api/v1/types/{type_code}/operations` - Get operations for type
- `GET /api/v1/operations/{id}` - Get operation by ID
- `POST /api/v1/types/{type_code}/operations` - Create operation
- `PUT /api/v1/operations/{id}` - Update operation
- `DELETE /api/v1/operations/{id}` - Delete operation

### Save All
- `POST /api/v1/save-all` - Save all changes in one transaction

## Database Schema

The application uses 4 main tables:

1. **process_type** - Process types (hierarchical)
2. **process_state** - States for each type
3. **process_operation** - Operations for each type
4. **process_operation_states** - Many-to-many relation (operation available in which states)

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Database Access

```bash
# Connect to database
docker exec -it swift-processing-db-1 psql -U postgres -d swift_processing

# View tables
\dt

# View data
SELECT * FROM process_type;
```

## Troubleshooting

### Port already in use

If port 5432, 8000, or 3000 is already in use:

1. Stop the service using that port
2. Or modify the port in docker-compose.yml or run commands

### Database connection error

Make sure PostgreSQL is running:

```bash
docker-compose ps
```

### Frontend can't connect to backend

Check that:
1. Backend is running on port 8000
2. CORS is configured correctly in backend/app/main.py
3. API_BASE_URL in frontend/src/api/client.ts matches backend URL

## Next Steps

See `PROCESS_MANAGER_APP_PLAN.md` for planned features and enhancements.

