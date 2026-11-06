# TaskFlow API

TaskFlow is a RESTful task management backend built with Python, FastAPI, SQLAlchemy, and SQLite. It provides user authentication and private task lists, with filtering, search, pagination, and automated API tests.

This repository is a backend-only application. It does not include a graphical frontend; the interactive Swagger UI at `/docs` can be used to explore and test the API.

## Features

- User registration with unique usernames and email addresses
- Password hashing with bcrypt
- Login using JWT bearer access tokens
- Create, retrieve, update, and delete tasks
- Separate task data for each authenticated user
- Task statuses: `todo`, `in_progress`, `done`
- Task priorities: `low`, `medium`, `high`
- Optional task descriptions and due dates
- Case-insensitive search by task title
- Filtering by status and priority
- Paginated task listings
- Request and response validation with Pydantic
- Interactive OpenAPI documentation and automated tests

## Technology stack

| Technology | Purpose |
| --- | --- |
| Python 3.11+ | Application language |
| FastAPI | REST API framework and OpenAPI documentation |
| Uvicorn | ASGI development server |
| SQLAlchemy 2 | ORM and database access |
| SQLite | Local relational database |
| Pydantic 2 | Data validation and serialization |
| python-jose | JWT creation and verification |
| passlib / bcrypt | Password hashing and verification |
| pytest / HTTPX | Automated API tests |

## Project structure

```text
taskflow/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Registration and login endpoints
│   │   └── tasks.py         # Task CRUD, filters, search, pagination
│   ├── __init__.py
│   ├── database.py          # Engine, session factory, database dependency
│   ├── dependencies.py      # Authenticated-user dependency
│   ├── main.py              # FastAPI setup, routes, application lifespan
│   ├── models.py            # SQLAlchemy User and Task models
│   ├── schemas.py           # Pydantic request/response schemas
│   └── security.py          # Password hashing and JWT utilities
├── tests/
│   ├── conftest.py          # Test database and client fixtures
│   └── test_api.py          # API tests
├── .env.example             # Example secret-key configuration
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting started

Run the following commands **from the directory containing `requirements.txt` and the `app` folder**.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, temporarily allow activation in the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Start the development server

```bash
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

| URL | Description |
| --- | --- |
| `http://127.0.0.1:8000/docs` | Interactive Swagger UI |
| `http://127.0.0.1:8000/redoc` | Alternative API documentation |
| `http://127.0.0.1:8000/health` | Health-check endpoint |

The SQLite database file `taskflow.db` is created automatically in the working directory when the application starts. Stop the server with `Ctrl+C`.

## Authentication workflow

### Register an account

**`POST /auth/register`** accepts a JSON request body:

```json
{
  "username": "alex",
  "email": "alex@example.com",
  "password": "secure-password-123"
}
```

The response contains the user's ID, username, email, and creation timestamp. Passwords are stored as hashes and are never returned in the response.

### Log in

**`POST /auth/login`** accepts `application/x-www-form-urlencoded` form data, **not JSON**:

```text
username=alex
password=secure-password-123
```

A successful login returns an access token:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Pass this token in the `Authorization` header when calling task endpoints:

```http
Authorization: Bearer <jwt-token>
```

In Swagger UI (`/docs`), click **Authorize**, enter the registered username and password in the OAuth2 form, and authorize. You can then execute the protected task endpoints directly from the browser.

Access tokens expire after 24 hours. The application does not currently implement refresh tokens or logout/token revocation.

## API reference

### Public endpoints

| Method | Endpoint | Description | Success status |
| --- | --- | --- | --- |
| `GET` | `/` | Basic application information | `200` |
| `GET` | `/health` | Health check | `200` |
| `POST` | `/auth/register` | Register a user | `201` |
| `POST` | `/auth/login` | Authenticate and receive a JWT | `200` |

### Protected task endpoints

All endpoints below require a valid bearer token.

| Method | Endpoint | Description | Success status |
| --- | --- | --- | --- |
| `POST` | `/tasks` | Create a task | `201` |
| `GET` | `/tasks` | List the current user's tasks | `200` |
| `GET` | `/tasks/{task_id}` | Retrieve a task | `200` |
| `PATCH` | `/tasks/{task_id}` | Partially update a task | `200` |
| `DELETE` | `/tasks/{task_id}` | Delete a task | `204` |

### Create a task

**`POST /tasks`** example body:

```json
{
  "title": "Prepare for a Python interview",
  "description": "Review SQL joins and API testing",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2026-12-01T18:00:00Z"
}
```

Only `title` is required. Defaults are `status: "todo"`, `priority: "medium"`, and `null` for the optional fields. Task responses also include the task ID and creation/update timestamps.

### List, filter, and search tasks

**`GET /tasks`** supports these query parameters:

| Parameter | Accepted values | Default |
| --- | --- | --- |
| `status` | `todo`, `in_progress`, `done` | No filter |
| `priority` | `low`, `medium`, `high` | No filter |
| `search` | Title search string (1–120 characters) | No search |
| `page` | Integer >= 1 | `1` |
| `page_size` | Integer from 1 to 100 | `10` |

Example requests:

```http
GET /tasks?status=todo
GET /tasks?priority=high&search=python
GET /tasks?status=in_progress&page=2&page_size=5
```

Results are ordered by creation time (newest first). The response is an object containing `items`, `total`, `page`, and `page_size`:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 10
}
```

### Update a task

**`PATCH /tasks/{task_id}`** updates only the fields supplied in the request:

```json
{
  "status": "done",
  "priority": "low"
}
```

### Delete a task

**`DELETE /tasks/{task_id}`** permanently deletes the selected task and returns HTTP `204 No Content` on success.

## Data model

### User

| Field | Description |
| --- | --- |
| `id` | Primary key |
| `username` | Unique username |
| `email` | Unique email address |
| `password_hash` | Hashed password |
| `created_at` | Account creation timestamp |

### Task

| Field | Description |
| --- | --- |
| `id` | Primary key |
| `title` | Required task title (1–120 characters, not blank) |
| `description` | Optional description (up to 2,000 characters) |
| `status` | Task status |
| `priority` | Task priority |
| `due_date` | Optional due date/time |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |
| `owner_id` | Foreign key referencing the user |

Each task belongs to one user. Queries for individual tasks include the authenticated user's ID, so users cannot retrieve, edit, or delete other users' tasks. Requests for tasks that do not belong to the current user return `404 Not Found`.

## How the application works

1. **Application startup:** `app/main.py` creates the FastAPI application, registers routers, configures CORS, and creates database tables if they do not already exist.
2. **Database access:** `app/database.py` configures the SQLite engine and provides a SQLAlchemy session to request handlers through FastAPI dependency injection.
3. **Validation:** `app/schemas.py` defines request and response formats, including allowed status/priority values and title validation.
4. **Authentication:** `app/routers/auth.py` handles registration and login; `app/security.py` hashes passwords and creates/verifies JWTs.
5. **Authorization:** `app/dependencies.py` extracts the bearer token, validates it, and loads the current user from the database.
6. **Task operations:** `app/routers/tasks.py` performs CRUD operations and applies ownership checks, search filters, and pagination.
7. **Persistence:** `app/models.py` defines the relational database entities and the one-to-many relationship between users and tasks.

## Running tests

With the virtual environment activated, run:

```bash
python -m pytest -v
```

The test suite uses a separate test database configuration and exercises API behavior without relying on the normal application database. The tests are located in `tests/test_api.py`.

## Configuration and security

The application reads its JWT signing secret from the `TASKFLOW_SECRET_KEY` environment variable. The repository includes `.env.example` as a reference, but **the application does not automatically load `.env` files**.

For example, set the secret in PowerShell before starting the server:

```powershell
$env:TASKFLOW_SECRET_KEY = "replace-with-a-long-random-secret-value"
python -m uvicorn app.main:app --reload
```

For macOS / Linux:

```bash
export TASKFLOW_SECRET_KEY="replace-with-a-long-random-secret-value"
python -m uvicorn app.main:app --reload
```

**Development limitations:** This is a learning and portfolio project, not a production-hardened service. The default JWT secret is insecure for public deployment; CORS currently allows all origins; SQLite is configured for local use; and database tables are created with `create_all()` rather than versioned migrations. Before public deployment, configure a strong secret, restrict CORS, use HTTPS, introduce migrations, and review authentication, logging, and rate limiting.

## Possible improvements

- Add Alembic database migrations
- Support PostgreSQL for deployment
- Add Docker and Docker Compose
- Add CI checks with GitHub Actions
- Implement refresh tokens and token revocation
- Add task sorting, categories, and tags
- Expand integration and edge-case tests
- Build a separate frontend application

## License

No license is specified in this repository.
