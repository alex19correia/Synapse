import typer
from src.config.settings import get_settings

cli = typer.Typer()
settings = get_settings()

@cli.command()
def start(
    host: str = settings.api_host,
    port: int = settings.api_port,
    reload: bool = True
):
    """Start the API server."""
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload
    )

@cli.command()
def test():
    """Run tests."""
    import pytest
    pytest.main(["tests", "-v"]) 