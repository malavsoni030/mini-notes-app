# Mini Notes App

A lightweight, full-stack note-taking application designed for creating, editing, and managing notes. The application features a clean, responsive React frontend connected to a FastAPI backend that persists data in a PostgreSQL (Supabase) database via SQLAlchemy.

---

## Tech Stack

- **Frontend**: React 19, Vite, Plain CSS (fully responsive, hand-crafted layout)
- **Backend**: FastAPI, Uvicorn, Pydantic v2
- **Database & ORM**: PostgreSQL (Supabase), SQLAlchemy 2.0, `psycopg2-binary`
- **Environment Management**: `python-dotenv`, Vite environment variables

---

## Folder Structure

```text
mini-notes-app/
├── backend/
│   ├── .env.example         # Template for backend environment variables
│   ├── check_db.py          # Standalone database connectivity check script
│   ├── database.py          # SQLAlchemy engine, session maker, and get_db dependency
│   ├── main.py              # FastAPI application, CORS setup, and API routes
│   ├── models.py            # SQLAlchemy ORM model (Note)
│   ├── requirements.txt     # Python backend dependencies
│   └── schemas.py           # Pydantic request and response schemas
├── frontend/
│   ├── .env.example         # Template for frontend environment variables
│   ├── index.html           # Single-page HTML entry point
│   ├── package.json         # Frontend dependencies and npm scripts
│   ├── vite.config.js       # Vite configuration with React plugin
│   └── src/
│       ├── api.js           # API client functions (getNotes, createNote, etc.)
│       ├── App.jsx          # Main React component (state, forms, note cards)
│       ├── App.css          # App-specific layout, card grid, and banner styles
│       ├── index.css        # Base CSS reset and typography
│       └── main.jsx         # React DOM mount point
├── .gitignore               # Root gitignore for secrets, dependencies, and artifacts
└── README.md                # Project documentation and setup guide
```

---

## Prerequisites

Before running the application locally, ensure you have the following installed:

- **Python**: Version 3.12 or 3.13
- **Node.js**: LTS version (v18 or higher recommended)
- **Git**: Latest version

---

## Backend Setup

### 1. Navigate to the backend directory
```bash
cd backend
```

### 2. Create a virtual environment

- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  ```

### 3. Activate the virtual environment

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install backend dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables

Copy the example environment file:

- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

Open `.env` and fill in your actual PostgreSQL database connection string:
```env
DATABASE_URL=postgresql://postgres.<project-ref>:<your-password>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

### 6. Verify database connectivity (Optional)
```bash
python check_db.py
```
*Expected output: `Database connection OK` and the number of rows.*

### 7. Run the FastAPI development server
```bash
uvicorn main:app --reload --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

---

## Frontend Setup

### 1. Navigate to the frontend directory
Open a new terminal window or tab:
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables

Copy the example environment file:

- **Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

Verify that `.env` contains the backend URL:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 4. Start the frontend development server
```bash
npm run dev
```

Open `http://localhost:5173` in your browser to use the Notes App.

---

## API Endpoints

| Method | Endpoint | Status Code | Description | Request Body | Response Body |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | `200 OK` | Health check | None | `{"status": "ok"}` |
| `GET` | `/api/notes` | `200 OK` | Retrieve all notes | None | Array of `NoteResponse` objects |
| `POST` | `/api/notes` | `201 Created` | Create a new note | `{"title": "string", "content": "string"}` | Created `NoteResponse` object |
| `PUT` | `/api/notes/{id}` | `200 OK` | Update note; refreshes `updated_at` | `{"title": "string", "content": "string"}` | Updated `NoteResponse` (or `404`) |
| `DELETE` | `/api/notes/{id}` | `204 No Content` | Delete note by ID | None | *No body* (or `404`) |

### Validation Rules
- `title`: Required, automatically trimmed of whitespace. A blank or whitespace-only title returns `422 Unprocessable Entity`.
- `content`: Optional, defaults to an empty string (`""`).

---

## Security & Environment Notice

> **Important**: Real `.env` files containing sensitive credentials, database URLs, and API keys are **never** committed to version control. The root `.gitignore` is configured to ignore all `.env` and `.env.*` files while keeping `.env.example` templates tracked. Always use `.env.example` as a template when setting up new environments.
