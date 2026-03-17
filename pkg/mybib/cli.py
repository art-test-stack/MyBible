"""Command-line interface for bibliography management."""

import argparse
import sys

from .arxiv import fetch_arxiv_metadata
from .bibtex import generate_bibtex
from .categories import (
    get_or_create_category,
    list_categories,
    load_categories,
    save_categories,
)
from .graph import build_citation_graph, export_graph_html
from .markdown import make_markdown_table, make_markdown_tables_by_category
from .scholar import search_and_confirm_article
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


def prompt_for_category(title: str, category_arg: str = None) -> str:
    """Prompt user to select or create a category.

    Args:
        title: Article title for context
        category_arg: Pre-specified category (used if provided)

    Returns:
        Category name
    """
    if category_arg:
        # If category argument provided, validate or create it
        categories = load_categories()
        cat_id, categories = get_or_create_category(category_arg, categories)
        save_categories(categories)
        return categories[cat_id]

    # Show existing categories and allow selection or creation
    categories = load_categories()
    cat_list = list_categories(categories)

    console.print("\n[bold]Available categories:[/]")
    for cat_id, cat_name in cat_list:
        console.print(f"  {cat_id}: {cat_name}")

    # Prompt for selection
    while True:
        choice = console.input(
            f"\n[bold]Select category ID for '{title}'[/] "
            "(or enter new category name): "
        ).strip()

        if choice.isdigit() and choice in categories:
            return categories[choice]
        elif choice:
            # Create new category
            cat_id, categories = get_or_create_category(choice, categories)
            save_categories(categories)
            console.print(f"[green]Created category '{choice}' with ID {cat_id}[/]")
            return categories[cat_id]
        else:
            console.print("[yellow]Please enter a valid category ID or name[/]")


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

    # Get category using new category system
    category = prompt_for_category(metadata["title"], args.category)

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
        arxiv_id=metadata.get("arxiv_id"),
        file_path=args.file,
    )
    print_success(f"Added: {metadata['title']}")


def handle_add_scholar(args) -> None:
    """Handle the add-scholar command to search Google Scholar.

    Args:
        args: Parsed command-line arguments
    """
    title = args.title
    url = args.url

    print_info("Searching Google Scholar for your article...")

    # If no title provided, try to extract from URL or abort
    if not title and not url:
        print_error("Either --title or --url must be provided")
        sys.exit(1)

    # Search query: use title if provided, else use URL
    search_query = title if title else url

    # Search and get confirmation from user
    metadata = search_and_confirm_article(search_query)

    if not metadata:
        print_error("Could not find or confirm article on Google Scholar")
        sys.exit(1)

    # Get category using new category system
    category = prompt_for_category(metadata["title"], args.category)

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
        doi=metadata.get("doi"),
        link=metadata.get("link"),
        category=category,
        scholar_id=metadata.get("scholar_id"),
        file_path=args.file,
    )
    print_success(f"Added: {metadata['title']}")


def handle_add_manual(args) -> None:
    """Handle the add command for manual reference entry.

    If only title is provided, searches Google Scholar automatically.
    All fields except title are optional.

    Args:
        args: Parsed command-line arguments
    """
    # Check if we need to search Google Scholar
    # If only title and category are provided (other fields are None), search Scholar
    has_manual_metadata = any(
        [
            args.authors,
            args.journal,
            args.year,
            args.doi,
            args.link,
        ]
    )

    if not has_manual_metadata:
        # Only title provided, search Google Scholar
        print_info("Searching Google Scholar for your article...")
        metadata = search_and_confirm_article(args.title)

        if not metadata:
            print_error("Could not find or confirm article on Google Scholar")
            sys.exit(1)
    else:
        # Use manually provided metadata
        metadata = {
            "title": args.title,
            "authors": args.authors or "",
            "journal": args.journal or "",
            "year": args.year,
            "doi": args.doi,
            "link": args.link or "",
        }

    # Get category using new category system
    category = prompt_for_category(metadata["title"], args.category)

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
        f"Add '[bold cyan]{metadata['title']}[/]' to [yellow]{category}[/]?"
    ):
        print_warning("Aborted.")
        sys.exit(0)

    add_reference(
        title=metadata["title"],
        authors=metadata.get("authors") or None,
        journal=metadata.get("journal") or None,
        year=metadata.get("year"),
        doi=metadata.get("doi"),
        link=metadata.get("link"),
        category=category,
        scholar_id=metadata.get("scholar_id"),
        file_path=args.file,
    )
    print_success(f"Added: {metadata['title']}")


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
    """Handle the graph command to build and visualize citations.

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


def handle_db_init(args) -> None:
    """Handle database initialization.

    Args:
        args: Parsed command-line arguments
    """
    from .db_storage import DatabaseStorage

    print_info(f"Initializing database: {args.db_url}")

    try:
        DatabaseStorage(args.db_url)
        print_success("Database initialized successfully!")
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        sys.exit(1)


def handle_db_migrate(args) -> None:
    """Handle migration from CSV to database.

    Args:
        args: Parsed command-line arguments
    """
    from .db_storage import DatabaseStorage

    print_info(f"Migrating from {args.file} to {args.db_url}")

    try:
        storage = DatabaseStorage(args.db_url)
        stats = storage.migrate_from_csv(args.file)

        console.print("\n[bold]Migration Statistics:[/]")
        console.print(f"  Total: {stats['total']}")
        console.print(f"  Added: {stats['added']}")
        console.print(f"  Duplicates: {stats['duplicates']}")
        console.print(f"  Errors: {stats['errors']}")

        print_success("Migration completed!")
    except Exception as e:
        print_error(f"Failed to migrate database: {e}")
        sys.exit(1)


def handle_db_export(args) -> None:
    """Handle export from database to CSV.

    Args:
        args: Parsed command-line arguments
    """
    from .db_storage import DatabaseStorage

    print_info(f"Exporting from {args.db_url} to {args.output}")

    try:
        storage = DatabaseStorage(args.db_url)
        count = storage.export_to_csv(args.output)
        print_success(f"Exported {count} references to {args.output}")
    except Exception as e:
        print_error(f"Failed to export database: {e}")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="mybib",
        description="📚 Manage research paper references with ease. "
        "Similar to gh, poetry, and uv!",
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

    # add-scholar command
    add_scholar_parser = subparsers.add_parser(
        "add-scholar", help="Add a reference from Google Scholar"
    )
    add_scholar_parser.add_argument("--title", help="Article title to search for")
    add_scholar_parser.add_argument("--url", help="Article URL to search for")
    add_scholar_parser.add_argument("--category", help="Category for the reference")
    add_scholar_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    add_scholar_parser.set_defaults(func=handle_add_scholar)

    # add command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a reference manually (or search Google Scholar"
        " if only title provided)",
    )
    add_parser.add_argument("--title", required=True, help="Article title (required)")
    add_parser.add_argument("--authors", help="Comma-separated author names")
    add_parser.add_argument("--journal", help="Journal or publication name")
    add_parser.add_argument("--year", type=int, help="Publication year")
    add_parser.add_argument("--doi", help="DOI identifier")
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

    # db-init command
    db_init_parser = subparsers.add_parser(
        "db-init", help="Initialize database for bibliography management"
    )
    db_init_parser.add_argument(
        "--db-url",
        default="sqlite:///bibliography.db",
        help="Database URL (default: sqlite:///bibliography.db)",
    )
    db_init_parser.set_defaults(func=handle_db_init)

    # db-migrate command
    db_migrate_parser = subparsers.add_parser(
        "db-migrate", help="Migrate references from CSV to database"
    )
    db_migrate_parser.add_argument(
        "--file",
        default="references.csv",
        help="CSV file path (default: references.csv)",
    )
    db_migrate_parser.add_argument(
        "--db-url",
        default="sqlite:///bibliography.db",
        help="Database URL (default: sqlite:///bibliography.db)",
    )
    db_migrate_parser.set_defaults(func=handle_db_migrate)

    # db-export command
    db_export_parser = subparsers.add_parser(
        "db-export", help="Export database references to CSV"
    )
    db_export_parser.add_argument("--output", required=True, help="Output CSV file")
    db_export_parser.add_argument(
        "--db-url",
        default="sqlite:///bibliography.db",
        help="Database URL (default: sqlite:///bibliography.db)",
    )
    db_export_parser.set_defaults(func=handle_db_export)

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
