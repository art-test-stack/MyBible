# argparse interface
import argparse
from .arxiv import fetch_arxiv_metadata
from .storage import add_reference
from .markdown import make_markdown_table, make_markdown_tables_by_category

def main():

    parser = argparse.ArgumentParser(
        prog="My Bible",
        description="Manage research paper references."
    )

    subparsers = parser.add_subparsers(dest="command")

    add_arxiv_parser = subparsers.add_parser("add-arxiv")
    add_arxiv_parser.add_argument("arxiv_url")
    add_arxiv_parser.add_argument("--category")
    add_arxiv_parser.add_argument("--file", default="references.csv")

    md_parser = subparsers.add_parser("markdown")
    md_parser.add_argument("--by-category", action="store_true")

    args = parser.parse_args()

    if args.command == "add-arxiv":
        handle_add_arxiv(args)

    elif args.command == "markdown":
        handle_markdown(args)

    else:
        parser.print_help()