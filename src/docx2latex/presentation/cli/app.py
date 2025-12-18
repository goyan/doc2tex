"""
CLI application using Typer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from docx2latex import __version__
from docx2latex.application.dto.conversion_options import ConversionOptions
from docx2latex.application.services.conversion_service import ConversionService
from docx2latex.shared.logging import setup_logging

# Create CLI app
app = typer.Typer(
    name="docx2latex",
    help="Convert DOCX documents to LaTeX with high-quality math support.",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"docx2latex version {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """DOCX to LaTeX converter with high-quality math support."""
    pass


@app.command()
def convert(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input DOCX file to convert.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output LaTeX file path. Defaults to input filename with .tex extension.",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-d",
            help="Output directory. Images will be saved in a subdirectory.",
        ),
    ] = None,
    image_dir: Annotated[
        str,
        typer.Option(
            "--image-dir",
            help="Subdirectory name for images.",
        ),
    ] = "images",
    document_class: Annotated[
        str,
        typer.Option(
            "--class",
            "-c",
            help="LaTeX document class.",
        ),
    ] = "article",
    font_size: Annotated[
        int,
        typer.Option(
            "--font-size",
            help="Base font size in points.",
        ),
    ] = 11,
    no_images: Annotated[
        bool,
        typer.Option(
            "--no-images",
            help="Don't extract images.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-V",
            help="Verbose output.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Debug mode with detailed logging.",
        ),
    ] = False,
) -> None:
    """
    Convert a DOCX file to LaTeX.

    Examples:

        docx2latex convert document.docx

        docx2latex convert document.docx -o output.tex

        docx2latex convert document.docx -d output_folder/
    """
    # Setup logging
    setup_logging(verbose=verbose or debug)

    # Build options
    options = ConversionOptions(
        output_path=output,
        output_dir=output_dir,
        image_dir=image_dir,
        document_class=document_class,
        font_size=font_size,
        extract_images=not no_images,
        verbose=verbose,
        debug=debug,
    )

    # Create service and convert
    service = ConversionService()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Converting...", total=None)

        result = service.convert(input_file, options)

    # Display results
    if result.success:
        console.print()
        console.print(
            Panel(
                f"[green]Successfully converted to:[/green]\n{result.output_path}",
                title="Conversion Complete",
                border_style="green",
            )
        )

        # Show statistics
        stats_table = Table(title="Statistics", show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Paragraphs", str(result.paragraph_count))
        stats_table.add_row("Tables", str(result.table_count))
        stats_table.add_row("Images", str(result.image_count))
        stats_table.add_row("Math blocks", str(result.math_count))
        stats_table.add_row("Time", f"{result.total_time_ms:.0f}ms")

        console.print(stats_table)

        # Show warnings if any
        if result.warnings:
            console.print()
            console.print(f"[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings[:5]:
                console.print(f"  - {warning}")
            if len(result.warnings) > 5:
                console.print(f"  ... and {len(result.warnings) - 5} more")

    else:
        console.print()
        console.print(
            Panel(
                f"[red]Conversion failed:[/red]\n{result.errors[0] if result.errors else 'Unknown error'}",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command()
def info(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="DOCX file to inspect.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
) -> None:
    """
    Show information about a DOCX file without converting.
    """
    from docx2latex.infrastructure.parsing.docx_parser import DocxParser
    from docx2latex.shared.result import Err

    parser = DocxParser()
    result = parser.parse(input_file)

    if isinstance(result, Err):
        console.print(f"[red]Error parsing file:[/red] {result.error}")
        raise typer.Exit(1)

    doc = result.value

    console.print()
    console.print(Panel(f"[bold]{input_file.name}[/bold]", title="Document Info"))

    # Metadata
    meta_table = Table(title="Metadata", show_header=False, box=None)
    meta_table.add_column("Field", style="cyan")
    meta_table.add_column("Value", style="white")

    if doc.metadata.title:
        meta_table.add_row("Title", doc.metadata.title)
    if doc.metadata.author:
        meta_table.add_row("Author", doc.metadata.author)
    if doc.metadata.created:
        meta_table.add_row("Created", doc.metadata.created)

    console.print(meta_table)

    # Statistics
    stats_table = Table(title="Content", show_header=False, box=None)
    stats_table.add_column("Element", style="cyan")
    stats_table.add_column("Count", style="white")

    stats_table.add_row("Sections", str(len(doc.sections)))
    stats_table.add_row("Paragraphs", str(doc.paragraph_count))
    stats_table.add_row("Tables", str(doc.table_count))
    stats_table.add_row("Images", str(doc.image_count))
    stats_table.add_row("Math blocks", str(doc.math_count))

    console.print(stats_table)

    # Page layout
    layout = doc.primary_layout
    console.print(f"\n[cyan]Page layout:[/cyan] {layout}")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
