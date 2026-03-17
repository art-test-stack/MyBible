"""UI utilities using rich for enhanced terminal output."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.prompt import Confirm
import pandas as pd

# Create a global console instance for consistent styling
console = Console()


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"✓ {message}", style="bold green")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"✗ {message}", style="bold red")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"⚠ {message}", style="bold yellow")


def print_info(message: str) -> None:
    """Print an info message in blue with emphasis."""
    console.print(f"ℹ {message}", style="bold blue")


@contextmanager
def progress_context(description: str = "Processing") -> Generator:
    """Context manager for showing progress during operations.
    
    Usage:
        with progress_context("Fetching metadata"):
            # Long-running operation
            pass
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task(description, total=None)
        try:
            yield
        finally:
            progress.stop()


@contextmanager
def api_progress() -> Generator:
    """Context manager for showing progress during API calls."""
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task("[cyan]Fetching from API...", total=None)
        try:
            yield
        finally:
            progress.stop()


def confirm_action(prompt: str, default: bool = True) -> bool:
    """Show a confirmation prompt with rich styling.
    
    Args:
        prompt: The question to ask
        default: Default response if user just presses enter (default: True)
        
    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(prompt, default=default, console=console)


def create_references_table(df: pd.DataFrame) -> Table:
    """Create a rich Table from a DataFrame of references.
    
    Args:
        df: DataFrame with columns: Title, Authors, Journal, Year, Category
        
    Returns:
        A rich Table object
    """
    table = Table(
        title="References",
        show_header=True,
        header_style="bold magenta",
        row_styles=["", "dim"],
        padding=(0, 1),
        show_lines=False,
    )
    
    # Add columns
    table.add_column("Title", style="cyan", width=40, overflow="fold")
    table.add_column("Authors", style="green", width=30, overflow="fold")
    table.add_column("Year", justify="center", width=6)
    table.add_column("Category", style="yellow", width=15)
    table.add_column("Journal", style="blue", width=20, overflow="fold")
    
    # Add rows
    for _, row in df.iterrows():
        table.add_row(
            str(row.get("Title", ""))[:40],
            str(row.get("Authors", ""))[:30],
            str(row.get("Year", "")),
            str(row.get("Category", "")),
            str(row.get("Journal", ""))[:20],
        )
    
    return table


def display_reference_preview(metadata: dict) -> None:
    """Display a nice preview of a reference before adding.
    
    Args:
        metadata: Dictionary with title, authors, journal, year, category
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    
    table.add_row("[bold cyan]Title:[/]", metadata.get("title", "N/A"))
    table.add_row("[bold cyan]Authors:[/]", metadata.get("authors", "N/A"))
    table.add_row("[bold cyan]Journal:[/]", metadata.get("journal", "N/A"))
    table.add_row("[bold cyan]Year:[/]", str(metadata.get("year", "N/A")))
    table.add_row("[bold cyan]DOI:[/]", metadata.get("doi", "N/A"))
    
    console.print(table)
