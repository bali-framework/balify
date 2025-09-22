import os

from fastapi import FastAPI
import typer
import uvicorn

app = typer.Typer()


@app.callback()
def callback():
    """Start Balify App"""


@app.command()
def dev():
    # os.system("python3 main.py")
    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"Hello": "World", "Powered by": "balify"}

    uvicorn.run(
        app,
        # "main:app",
        # host=self.http_host,  # fix for docker port mapping
        # port=self.http_port,
        # reload=True,
        access_log=True,
        reload_excludes=["*.log"],
    )
