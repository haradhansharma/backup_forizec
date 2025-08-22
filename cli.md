# Usefull commands for forizec project

## **Black** and **Ruff** Section
This section contains helpfull commands for formatting, linting and maintainning code quality using **Black** and **Ruff**
---

### Check formatting / linting
#### **Black** (Check only, does not modify files)
```bash
black --check
```
#### **Ruff** (Lint only, does not modify files)
```bash
ruff check .
# or using the new config section
ruff lint .
```

### Auto-Formate / Fix Issues
#### **Black** (Formate file in place)
```bash
black .
```
#### **Ruff** (Auto-fix fixable issues)
```bash
ruff check . --fix
```
### Combined workflow (opional)
Run both linters in one go
```bash
black --check .
ruff check .
```
Or auto-fix everything:
```bash
black .
ruff check . --fix
```
### Useful Flags
- `--diff` -> Show what would change without applying (Black)
```bash
black --diff .
```
- `select` / `ignore` -> Override pyproject.toml temporarily (Ruff)
```bash
ruff check . --select E,F
```
### Optional: Pre-commit Hook
You can setup a pre-commit hook to autometically run Black + Ruff before each commit to mintain code quality.
```bash
pre-commit install
pre-commit run --all-files
```

## Forizec CLI command section

This section provides detailed information about the **Forizec CLI** built with typer. The CLi helps manage database migrations, run the server, access an interactive shell, print DB URLS, and run tests.
---

### Database Commands
#### **Create new migrations**
```bash
python forizec.py makemigrations "Migration message"
```
Automatically generates a new alembic migration based on model changes.

#### **Apply Migrations**
```bash
python forizec.py migrate
# or with a custom auto-message
python forizec.py migrate "Auto migration message"
```
Applies pending migrations to the database.

#### **Rollback Migrations**
```bash
python forizec.py rollback 1
```
Rollback the last N migrations. Default is 1.

#### **Show Migration History***
```bash
python forizec.py history
```
Displays the full migration history.

#### **Show Current Migration***
```bash
python forizec.py current
```
Show the current migration version.

#### **Show Current Heads***
```bash
python forizec.py heads
```
Displays current heads of the migration hsitory.

### **Server and Shell commands***
#### **Run FastAPI Server**
```bash
python forizec.py runserver --host 127.0.0.1 --port 8017 --reload
```
- Runs the FastAPI server using Uvicorn
- `--reload` enables auto-reload on code changes.

#### **Open Interactive Python Shell**
```bash
python forizec.py shell
```
- Opens a Python shell with the project context preloaded, including settings and placeholders for models and DB session.

#### **Print Database URL**
```bash
python forizec.py dburl
```
- Print the current database url configured in `.env` or settings.

### **Test Commands**
#### **Run relationshi Tests**
```bash
python forizec.py test-relationships
# Optionally run only failed tests first
python forizec.py test-relationships --k
```
- Tests database model relationships and integrity.

#### **Run API Route Tests**
```bash
python forizec.py test-api
```
- Tests all JSON API endpoints (GET, POST, PUT, PATCH, DELETE).

#### **Run HTML Route Tests**
```bash
python forizec.py test-html
```
- Tests all HTML endpoints and templates rendering.

#### **Run End-to-End Playwright Tests**
```bash
python forizec.py test-e2e
# Run in non-headless mode for debugging
python forizec.py test-e2e --headless False
```
- Execute Browser based workflows using Playwright.

#### **Run all Tests**
```bash
python forizec.py test-all

```
- Run all test suites: database relationships, API, HTML, and E2E.

### **Notes**
- **Environment Variables:**
You can override the database url or Playwright headless mode using environment variables:
```bash
export DATABASE_URL="sqlite+aiosqlite:///./data/forizec_test.db"
export HEADLESS=false
```
- **Customization:** The CLI is modular -- you can add more commands or extend existing ones for your project workflows.
- **Output:** All commands use Rich for colored console output, giving clear visual feedback during execution.
