"""CLI module."""
import click
import asyncio
from typing import Optional
import httpx
from rich.console import Console
from src.config.settings import get_settings
from src.chat.chat_service import ChatService

console = Console()

@click.group()
@click.version_option()
def cli():
    """Synapse CLI."""
    pass

@cli.command()
@click.option("--output", type=click.Choice(["text", "json"]), default="text")
def config(output: str):
    """Show configuration."""
    settings = get_settings()
    if output == "json":
        console.print_json(settings.model_dump())
    else:
        for key, value in settings.model_dump().items():
            console.print(f"{key}: {value}")

@cli.command()
@click.argument("query")
@click.option("--model", help="Model to use")
@click.option("--temperature", type=float, help="Temperature for generation")
@click.option("--stream/--no-stream", default=True, help="Stream output")
def chat(query: str, model: Optional[str], temperature: Optional[float], stream: bool):
    """Chat with the assistant."""
    settings = get_settings()
    chat_service = ChatService(settings)
    
    async def run_chat():
        try:
            if stream:
                async for chunk in chat_service.stream_chat(query, model, temperature):
                    console.print(chunk, end="")
                console.print()  # New line at end
            else:
                result = await chat_service.chat(query, model, temperature)
                console.print(result["response"])
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            
    asyncio.run(run_chat())

@cli.command()
def verify():
    """Verify connections to all services."""
    settings = get_settings()
    
    async def check_connections():
        try:
            # Check Redis
            import redis.asyncio as redis
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            console.print("[green]✓[/green] Redis connection successful")
        except Exception as e:
            console.print(f"[red]✗[/red] Redis connection failed: {e}")
            
        try:
            # Check Qdrant
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{settings.QDRANT_URL}/healthz")
                if response.status_code == 200:
                    console.print("[green]✓[/green] Qdrant connection successful")
                else:
                    console.print("[red]✗[/red] Qdrant health check failed")
        except Exception as e:
            console.print(f"[red]✗[/red] Qdrant connection failed: {e}")
            
        try:
            # Check Supabase
            from supabase import create_client
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            response = supabase.auth.get_user()
            console.print("[green]✓[/green] Supabase connection successful")
        except Exception as e:
            console.print(f"[red]✗[/red] Supabase connection failed: {e}")
            
        try:
            # Test LLM
            chat_service = ChatService(settings)
            result = await chat_service.chat("test", None, None)
            console.print("[green]✓[/green] LLM connection successful")
        except Exception as e:
            console.print(f"[red]✗[/red] LLM connection failed: {e}")
    
    asyncio.run(check_connections())

if __name__ == "__main__":
    cli() 