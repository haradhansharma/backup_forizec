python -m venv env
# windows
- ./env.Scripts/activate
- python -m pip install --upgrade pop
in requirements.txt:
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
alembic
pydantic
pydantic-settings
aiosqlite
asyncpg
asyncmy
python-dotenv
httpx[http2]
pytest
pytest-asyncio
ruff
black

pip install -r requirements.txt
pip freeze > requirements.txt
curl https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore -o .gitignore

write .env
# Database configuration (SQLite in this case)
ENV=dev
DB_BACKEND=sqlite
DB_PATH=./data/forizec.db

# MySQL configuration (if using MySQL)
ENV=staging
DB_HOST=localhost
DB_BACKEND=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=''
DB_NAME=forizec

# POSTGRESQL configuration (if using PostgreSQL)
ENV=prod
DB_BACKEND=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres    
DB_PASSWORD=''
DB_NAME=forizec

comamnd python -c "import secrets; print(secrets.token_hex(32))"

SECRET_KEY=cfce7ae89103b425d6eca2d521bdaec8b260d90b3af32282bd4e2f8836a1abcc


#Typical commands
## create alembic scaffold (already done)
alembic init migrations

## create a revision (auto-detect changes)
alembic revision -m "create users table" --autogenerate

## upgrade to head
alembic upgrade head

## downgrade one step
alembic downgrade -1

If you maintain multiple .env.* files, set which one to use before running Alembic:
# Example: Linux/macOS
cp .env.dev .env
alembic upgrade head

# Or export the URL explicitly (overrides everything)
export DATABASE_URL="postgresql+asyncpg://postgres:@localhost:5432/forizec"
alembic upgrade head

Windows PowerShell:

$env:DATABASE_URL="postgresql+asyncpg://postgres:@localhost:5432/forizec"
alembic upgrade head


forizec
- app
-- main.py
-- api
---v1
---- routes
----- admin.py
----- auth.py
----- user.py
-- core
--- config.py
--- db.py
-- models
-- schemas
-- tests
-- uils
- data
- env
- media
- migrations
-- env.py
- static
- templates
- .env
- .gitignore
- alembic.ini
- requirements.txt
