# Usefull commands for forizec project

## **Environment preparation**
### Prepare development Environment
```bash
pyton forizec.py prepare
```
This command setup the local developement environment by performing the following steps:
- Create a python virtual environment (`env/`) if not already present.
- Install dependency from `requirements.txt`. **Will fail with clear message if the file is missing.**
- Install Playwright Browser
- Create project directory if missing:
    - `data/` -> store the SQLite DB and other runtime files.
    - `static/` -> serve static assets (CSS, JS, Images).
    - `media/` -> for user-uploaded media.
    - `templates` -> for HTML templates.
- Generate a `.env` file with the default placeholder if it does not exists.
- **Note:** This command is crossplatform aware and works on linux, macOS, and windows.
- **Idempotency:** Running `prepare` multiple times willnot overwrite existing folders or `.env`.




## **Black** and **Ruff** Section
This section contains helpfull commands for formatting, linting and maintainning code quality using **Black** and **Ruff**
---

### Check formatting / linting
#### **Black** (Check only, does not modify files)
```bash
black --check .
```
#### **Ruff** (Lint only, does not modify files)
```bash
ruff check .
# or You can also check a single file
ruff check app/main.py

```
**Note:** Older Ruff versions may have used `ruff lint .`, but the correct modern usage is `ruff check .`.



### Auto-Formate / Fix Issues
#### **Black** (Formate files in place)
```bash
black .
```
#### **Ruff** (Auto-fix fixable issues)
```bash
ruff check . --fix
# or You can also fix a single file
ruff check app/main.py --fix
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
ruff check . --ignore E501 # Ignore specific rules
```
### Check a specific file or folder
```bash
ruff check app/ # Lint the entire folder
ruff check app/main.py # Lint a single file
```

### Optional: Pre-commit Hook
You can setup a pre-commit hook to autometically run Black + Ruff before each commit to mintain code quality.
```bash
pre-commit install
pre-commit run --all-files
```
**Tip:** Combine this with .pre-commit-config.yaml to enforce formatting and linting in your CI/CD pipeline.

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
Before running tests, **ensure your server url, routes, or necessary fixures exists** (e.g., `api/v1/user/me`, login routes) and the database initialized properly.
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
- Use test data and headers where required, ensuring correct response status, content type, and response body.
- Example reference: `app/tests/test_api_routes.py`

#### **Run HTML Route Tests**
```bash
python forizec.py test-html
```
- Tests all HTML endpoints and templates rendering.
- Checks response code and expected test in rendered templates.

#### **Run End-to-End Playwright Tests**
```bash
python forizec.py test-e2e
# Run in non-headless mode for debugging
python forizec.py test-e2e --headless False
```
- Execute Browser based workflows using Playwright, validating full user interaction flows.

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
