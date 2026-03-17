"""Command-line interface for bibliography management."""

import argparse
import sys

from .arxiv import fetch_arxiv_metadata
from .bibtex import generate_bibtex
from .graph import build_citation_graph, export_graph_html
from .markdown import make_markdown_table, make_markdown_tables_by_category
from .storage import add_reference, load_references
from .ui import (
    api_progress,
    confirm_action,
    console,
    display_reference_preview,
    print_error,
    print_info,
    print_success,
    print_warning,
)


def handle_add_arxiv(args) -> None:
    """Handle the add-arxiv command.

    Args:
        args: Parsed command-line arguments
    """
    # Extract arxiv ID from URL
    arxiv_id = args.arxiv_url.split("/")[-1]

    # Fetch metadata from arXiv with progress indicator
    print_info(f"Fetching metadata for arXiv ID: {arxiv_id}")
    with api_progress():
        metadata = fetch_arxiv_metadata(arxiv_id)

    # Get category if not provided
    category = args.category
    if category is None:
        category = console.input(
            f"Enter category for '[bold cyan]{metadata['title']}[/]': "
        )

    category = category.lower().strip()

    # Show reference preview
    preview_data = {
        "title": metadata["title"],
        "authors": metadata["authors"],
        "journal": metadata["journal"],
        "year": metadata["year"],
        "doi": metadata["doi"],
    }
    console.print()
    display_reference_preview(preview_data)
    console.print()

    # Confirm before adding
    if not confirm_action(
        f"Add '[bold cyan]{metadata['title']}[/]' to category '[yellow]{category}[/]'?"
    ):
        print_warning("Aborted.")
        sys.exit(0)

    # Add reference to storage
    add_reference(
        title=metadata["title"],
        authors=metadata["authors"],
        journal=metadata["journal"],
        year=metadata["year"],
        doi=metadata["doi"],
        link=metadata["link"],
        category=category,
        file_path=args.file,
    )
    print_success(f"Added: {metadata['title']}")


def handle_add_manual(args) -> None:
    """Handle the add command for manual reference entry.

    Args:
        args: Parsed command-line arguments
    """
    # Show reference preview
    preview_data = {
        "title": args.title,
        "authors": args.authors,
        "journal": args.journal,
        "year": args.year,
        "doi": args.doi,
    }
    console.print()
    display_reference_preview(preview_data)
    console.print()

    # Confirm before adding
    msg = f"Add '[bold cyan]{args.title}[/]' to [yellow]{args.category}[/]?"
    if not confirm_action(msg):
        print_warning("Aborted.")
        sys.exit(0)

    add_reference(
        title=args.title,
        authors=args.authors,
        journal=args.journal,
        year=args.year,
        doi=args.doi,
        link=args.link,
        category=args.category,
        file_path=args.file,
    )
    print_success(f"Added: {args.title}")


def handle_markdown(args) -> None:
    """Handle the markdown command to generate markdown tables.

    Args:
        args: Parsed command-line arguments
    """
    print_info("Generating markdown tables...")

    if args.by_category:
        table = make_markdown_tables_by_category(args.file)
    else:
        table = make_markdown_table(args.file)

    if args.output:
        with open(args.output, "w") as f:
            f.write(table)
        print_success(f"Markdown written to {args.output}")
    else:
        console.print(table)


def handle_bibtex(args) -> None:
    """Handle the bibtex command to generate BibTeX file.

    Args:
        args: Parsed command-line arguments
    """
    print_info("Generating BibTeX...")
    df = load_references(args.file)
    bibtex_content = generate_bibtex(df)

    if args.output:
        with open(args.output, "w") as f:
            f.write(bibtex_content)
        print_success(f"BibTeX written to {args.output}")
    else:
        console.print(bibtex_content)


def handle_graph(args) -> None:
    """Handle the graph command to build and visualize citation graph.

    Args:
        args: Parsed command-line arguments
    """
    df = load_references(args.file)

    if df.empty:
        print_error(f"No references found in {args.file}")
        sys.exit(1)

    print_info(f"Building citation graph from {len(df)} references...")
    graph = build_citation_graph(df, output_references=args.verbose)

    output_file = args.output or "citation_graph.html"
    export_graph_html(graph, output_file)
    print_success(f"Citation graph exported to {output_file}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mybib",
        description=(
            "📚 Manage research paper references with ease. "
            "Similar to gh, poetry, and uv!"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mybib add-arxiv https://arxiv.org/abs/2301.00001 --category ML
  mybib add --title "My Paper" --authors "Author Name" --journal "Nature" \
    --year 2024 --doi "10.xxxx/xxxxx" --category Science
  mybib markdown --file references.csv --output README.md
  mybib bibtex --file references.csv --output references.bib
  mybib graph --file references.csv --output graph.html
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add-arxiv command
    add_arxiv_parser = subparsers.add_parser(
        "add-arxiv", help="Add a reference from an arXiv URL"
    )
    add_arxiv_parser.add_argument(
        "arxiv_url", help="The arXiv URL (e.g., https://arxiv.org/abs/2301.00001)"
    )
    add_arxiv_parser.add_argument("--category", help="Category for the reference")
    add_arxiv_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    add_arxiv_parser.set_defaults(func=handle_add_arxiv)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a reference manually")
    add_parser.add_argument("--title", required=True, help="Article title")
    add_parser.add_argument(
        "--authors", required=True, help="Comma-separated author names"
    )
    add_parser.add_argument(
        "--journal", required=True, help="Journal or publication name"
    )
    add_parser.add_argument("--year", required=True, type=int, help="Publication year")
    add_parser.add_argument("--doi", required=True, help="DOI identifier")
    add_parser.add_argument("--link", help="URL link to the resource")
    add_parser.add_argument("--category", help="Category for classification")
    add_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    add_parser.set_defaults(func=handle_add_manual)

    # markdown command
    md_parser = subparsers.add_parser(
        "markdown", help="Generate markdown tables from references"
    )
    md_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    md_parser.add_argument(
        "--by-category", action="store_true", help="Split tables by category"
    )
    md_parser.add_argument("--output", help="Output file (e.g., README.md)")
    md_parser.set_defaults(func=handle_markdown)

    # bibtex command
    bibtex_parser = subparsers.add_parser(
        "bibtex", help="Generate BibTeX file from references"
    )
    bibtex_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    bibtex_parser.add_argument("--output", help="Output file (e.g., references.bib)")
    bibtex_parser.set_defaults(func=handle_bibtex)

    # graph command
    graph_parser = subparsers.add_parser(
        "graph", help="Build and visualize citation graph"
    )
    graph_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    graph_parser.add_argument(
        "--output", help="Output HTML file (default: citation_graph.html)"
    )
    graph_parser.add_argument(
        "--verbose", action="store_true", help="Show verbose output references"
    )
    graph_parser.set_defaults(func=handle_graph)

    args = parser.parse_args()

    # Execute the appropriate handler or show help
    if hasattr(args, "func"):
        try:
            args.func(args)
        except KeyboardInterrupt:
            console.print()
            print_warning("Operation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            print_error(f"An error occurred: {e}")
            sys.exit(1)
    else:
        parser.print_help()
