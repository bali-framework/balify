import os
import sys

import logging
import importlib.util


from fastapi import FastAPI
import typer
import uvicorn

from pathlib import Path


app = typer.Typer()


def _find_main_py(cwd: Path) -> Path | None:
    candidate = cwd / "main.py"
    return candidate if candidate.is_file() else None


def _load_app_from_main(path: Path):
    # Try to prefer module import by name: if cwd is on sys.path, uvicorn can load "main:app"
    cwd = str(path.parent)
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    # Prefer returning module path string for uvicorn to import
    try:
        return "main:app"
    except Exception:
        pass

    # Fallback: load the file as a module and return the app object
    spec = importlib.util.spec_from_file_location("local_main", str(path))
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    if hasattr(module, "app"):
        return module.app
    raise RuntimeError("main.py found but no 'app' variable inside")


@app.callback()
def callback():
    """Start Balify App"""


@app.command()
def dev():
    # os.system("python3 main.py")
    app = FastAPI(title="Balify")

    if not os.path.isfile("main.py"):
        typer.secho(
            "No `main.py` found, start `hello world`.",
            fg=typer.colors.MAGENTA,
        )

        @app.get("/")
        def hello():
            return {"Hello": "World", "Powered by": "balify"}

        uvicorn.run(app)
    else:
        # Search current working directory for main.py and run its app with uvicorn.
        cwd = Path.cwd()
        main_path = _find_main_py(cwd)

        if not main_path:
            typer.secho(
                "Error: main.py not found in current directory.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=2)

        # Attempt to supply a module:path string to uvicorn, otherwise provide the app callable
        try:
            target = _load_app_from_main(main_path)
        except Exception as exc:
            typer.secho(f"Error loading app from main.py: {exc}", fg=typer.colors.RED)
            raise typer.Exit(code=3)

        typer.secho(f"Starting server with target={target}", fg=typer.colors.GREEN)
        uvicorn.run(
            target,
            # host=self.http_host,  # fix for docker port mapping
            # port=self.http_port,
            reload=True,
            access_log=True,
            reload_excludes=["*.log"],
        )
