import code
import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from app.core.config import settings

app = typer.Typer(help="Forizec CLI for managing Forizec projects.")
console = Console()

BASE_DIR = Path(settings.BASE_DIR)
VENV_DIR = BASE_DIR / "env"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"
ENV_FILE = BASE_DIR / ".env"
# ---------
# Utility helper
# ---------


def venv_bin(bin_name: str) -> Path:
    """Get the path to a binary inside the virtual environment."""
    if os.name == "nt":  # Windows
        return VENV_DIR / "Scripts" / bin_name
    else:  # Unix-like
        return VENV_DIR / "bin" / bin_name


def run_command(cmd: list[str], **kwargs):
    """Run subprocess command and log it to console."""
    console.print(f"[cyan]$ {' '.join(map(str, cmd))}[/cyan]")
    subprocess.run(cmd, check=True, **kwargs)


def run_alembic_command(*args: str, capture_output: bool = False):
    """Helper to run Alembic commands with correct config."""
    alembic_init = BASE_DIR / "alembic.ini"
    cmd = ["alembic", "-c", str(alembic_init), *args]
    console.print(f"[cyan]Running Alembic command:[/cyan] `{' '.join(cmd)}`")
    # typer.echo(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


# ---- CLI Preparation ----
@app.command()
def prepare():
    """
    Prepare the Forizec project for development:
    - create venv if missing
    - Install dependencies from requirements.txt
    - Install Playwright browsers
    - create data/, media/, static/, templates/ directories if missing
    - create .env file if missing
    """

    console.rule("[bold blue]Preparing Forizec Project[/bold blue]")

    # 1. Create virtual environment if missing
    if not VENV_DIR.exists():
        console.print("[yellow]Creating virtual environment ...[/yellow]")
        run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        console.print("[green]Virtual environment already exists.[/green]")

    # 2. Install dependencies from requirements.txt
    if REQUIREMENTS_FILE.exists():
        console.print("[yellow]Installing dependencies from requirements.txt ...[/yellow]")
        pip_path = venv_bin("pip")
        run_command([str(pip_path), "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        console.print(f"[red]requirements.txt not found at {REQUIREMENTS_FILE}[/red]")
        console.print(
            "[red]Cannot install dependencies. Please create a requirements.txt file.[/red]"
        )
        console.print("[red]Exiting...[/red]")
        raise typer.Exit(code=1)

    # 3. Install Playwright browsers
    console.print("[yellow]Installing Playwright browsers ...[/yellow]")
    run_command([str(venv_bin("playwright")), "install"])

    # 4. Create necessary directories if missing
    for dir_path in [
        settings.MEDIA_DIR,
        settings.STATIC_DIR,
        settings.TEMPLATES_DIR,
        BASE_DIR / "data",
    ]:
        if not dir_path.exists():
            console.print(f"[yellow]Creating directory: {dir_path} ...[/yellow]")
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            console.print(f"[green]Directory already exists: {dir_path}[/green]")

    # 5. Create .env file if missing
    if not ENV_FILE.exists():
        console.print("[yellow]Creating .env file with default settings ...[/yellow]")
        ENV_FILE.write_text(
            """
            # .env
            # Environment settings for Forizec
            # ---- app ---
            ENV=dev
            DEBUG=True
            SECRET_KEY=cfreate_a_secure_random_key_and_set_it_here
            # ---- database (sqlite) ---
            DATABASE_URL=sqlite+aiosqlite:///./data/forizec.db
            # ---- MySQL (staging) ---
            # DATABASE_URL=mysql+asyncmy://user:password@localhost:3306/forizec_db
            # ---- PostgreSQL (prod) ---
            # DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/forizec_db
            """
        )
        console.print(f"[green].env file created at {ENV_FILE}[/green]")
    else:
        console.print(f"[green].env file already exists at {ENV_FILE}[/green]")

    console.rule("[bold green]Forizec Project is ready![/bold green]")


# ---------
# Database commands
# ---------


@app.command()
def makemigrations(message: str = typer.Argument(..., help="Migration message")):
    """Create new migrations based on changes in the models."""
    console.print(f"[yellow]Creating new migration with message:[/yellow] [bold]{message}[/bold]")
    run_alembic_command("revision", "-m", message, "--autogenerate")
    console.print("[green]Migration created successfully.[/green]")


@app.command()
def migrate(
    auto_message: str = typer.Argument(
        "Auto migration", help="Message for auto-generated migration"
    )
):
    """Apply migrations to the database. If the database is behind autogenerate a migration first."""
    # check if database is behind
    # result = run_alembic_command("check", capture_output=True)
    # if "Target database is not up to date" in result.stdout:
    #     typer.echo("Database is behind, auto creating a new migration...")
    #     run_alembic_command("revision", "-m", auto_message, "-- Auto migration")
    # typer.echo("Applying migrations...")
    console.print(f"[yellow]Applying migrations with message:[/yellow] [bold]{auto_message}[/bold]")
    run_alembic_command("upgrade", "head")
    console.print("[green]Migrations applied successfully.[/green]")


@app.command()
def rollback(step: int = typer.Argument(1, help="Number of migrations to roll back")):
    """Roll back the last N migrations."""
    console.print(f"[yellow]Rolling back the last {step} migration(s)...[/yellow]")
    if step < 1:
        typer.echo("Step must be a positive integer.")
        raise typer.Exit(code=1)
    run_alembic_command("downgrade", f"-{step}")
    console.print("[green]Rollback completed successfully.[/green]")


@app.command()
def history():
    """Show the migration history."""
    run_alembic_command("history")


@app.command()
def current():
    """Show the current migration version."""
    run_alembic_command("current")


@app.command()
def heads():
    """Show the current heads of the migration history."""
    run_alembic_command("heads")


# ---------
# Extra utility commands
# ---------


@app.command()
def runserver(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
):
    """Run the Forizec FastAPi server with uvicorn."""
    command = [
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        command.append("--reload")

    typer.echo(f"Starting server at http://{host}:{port}")
    subprocess.run(command, check=True)


@app.command()
def shell():
    """Open an interactive Python shell with Forizec context."""
    banner = "Interactive Forizec shell. Type 'exit()' to leave."
    namespace = {
        "settings": settings,
        # can be added later
        "User": None,  # Placeholder for User model
        "SessionLocal": None,  # Placeholder for SessionLocal
        # Add any other models or utilities you want to expose in the shell
    }
    # typer.echo(banner)
    # Set up the environment for the shell
    sys.path.append(str(BASE_DIR))
    code.interact(local=namespace, banner=banner)


@app.command()
def dburl():
    """Print the database URL."""
    # typer.echo(f"Database URL: {settings.DATABASE_URL}")
    console.print(Markdown(f"**Database URL:** `{settings.DATABASE_URL}`"), style="bold green")


@app.command()
def test_relationships(
    k: bool = typer.Option(
        False, "--k", help="Run only failed tests first. (-k). This is useful for debugging."
    )
):
    """Run database model relationships tests."""
    console.print("[yellow]Running database relationships tests...[/yellow]")
    args = ["pytest", "app/tests/test_database_relations.py", "-v"]
    if k:
        args.append("-k")
    subprocess.run(args, check=True)
    console.print("[green]Database relationships tests completed successfully.[/green]")


@app.command()
def test_api():
    """Run tests for JSON API routes."""
    console.print("[yellow]Running API routes tests...[/yellow]")
    subprocess.run(["pytest", "app/tests/test_api_routes.py", "-v"], check=True)
    console.print("[green]API routes tests completed successfully.[/green]")


@app.command()
def test_html():
    """Run tests for HTML routes."""
    console.print("[yellow]Running HTML routes tests...[/yellow]")
    subprocess.run(["pytest", "app/tests/test_html_routes.py", "-v"], check=True)
    console.print("[green]HTML routes tests completed successfully.[/green]")


@app.command()
def test_e2e(
    headless: bool = typer.Option(True, "--headless", help="Run end-to-end tests in headless mode.")
):
    """Run end-to-end tests using Playwright."""
    console.print("[yellow]Running end-to-end tests with Playwright...[/yellow]")
    env = dict(**os.environ)
    if not headless:
        env["HEADLESS"] = "false"  # Let playwright fixure pick this up
    subprocess.run(["pytest", "app/tests/test_e2e_playwright.py", "-v"], check=True, env=env)
    console.print("[green]End-to-end tests completed successfully.[/green]")


@app.command()
def test_all():
    """Run all tests: relationships, API, HTML, and E2E."""
    console.print("[yellow]Running all tests...[/yellow]")
    subprocess.run(["pytest", "tests", "-v"], check=True)
    console.print("[green]All tests completed successfully.[/green]")


if __name__ == "__main__":
    app()
