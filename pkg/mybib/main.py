import pandas as pd
import requests
import argparse
import sys

import xml.etree.ElementTree as ET

# make a command line interface to add references in a csv file and generate markdown tables for the README.md file
# try from link to get article properties (title, authors, journal, year, doi) 
# -> arxiv API first (easier)
# add reference to .csv file
# turn into markdown table separated by category
# markdown table:
# | Title | Author(s) | Journal | Year | DOI | Link | Category |

def add_reference(
    title: str,
    authors: str,
    journal: str,
    year: int,
    doi: str,
    link: str,
    category: str,
    file_path: str = "references.csv",
) -> None:
    """Add a reference to the CSV file."""
    new_reference = {
        "Title": title,
        "Authors": authors,
        "Journal": journal,
        "Year": year,
        "DOI": doi,
        "Link": link,
        "Category": category,
    }
    row = pd.DataFrame([new_reference])
    is_new_file = not pd.io.common.file_exists(file_path)
    if not is_new_file:
        existing_df = pd.read_csv(file_path)
        if doi in [ str(d) for d in set(existing_df["DOI"].to_list()) ]:
            print("Reference already exists in the CSV file.")
            sys.exit(0)
    row.to_csv(file_path, mode="a", index=False, header=is_new_file)

def reform_names(s_authors: str) -> str:
    authors = s_authors.split(", ")
    if len(authors) > 2:
        first_author = authors[0].split()[-1]
        authors = f"{first_author} et al."
    elif len(authors) == 2:
        first_author = authors[0].split()[-1]
        second_author = authors[1].split()[-1]
        authors = f"{first_author} and {second_author}"
    else:
        authors = authors.split()[-1]
    return authors

def prepare_csv_file_to_md(file_path: str = "references.csv") -> pd.DataFrame:
    """Prepare the CSV file with headers if it doesn't exist."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Title", "Authors", "Journal", "Year", "DOI", "Link", "Category"])
        df.to_csv(file_path, index=False)
    df["Authors"] = df["Authors"].apply(reform_names)
    df["DOI"] = df.apply(lambda row: f"[{row.get("DOI", "unknown")}]", axis=1)
    df = df.sort_values(by=["Category", "Year"], ascending=[True, False])
    return df

def make_markdown_table(file_path: str = "references.csv") -> str:
    """Generate a markdown table from the CSV file."""
    df = prepare_csv_file_to_md(file_path)
    markdown_table = df.to_markdown(index=False)
    return markdown_table

def make_markdown_tables_by_category(file_path: str = "references.csv") -> str:
    """Generate markdown tables separated by category."""
    df = prepare_csv_file_to_md(file_path)
    footer = []
    output = []
    for category, group in df.groupby("Category"):
        output.append(f"## {category}\n")
        output.append(group.drop(columns=["Category", "Link"]).to_markdown(index=False))
        output.append("\n")
        footer.extend(f"{doi}: {link}" for doi, link in zip(group["DOI"], group["Link"]))
    footer = sorted(set(footer), key=lambda x: x.split(":")[0])  # sort by DOI
    return "\n".join(output) + "\n".join(footer)

def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """Fetch metadata from arxiv API."""
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching arxiv metadata: {response.status_code}")
        sys.exit(1)
    
    root = ET.fromstring(response.content)
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    entry = root.find('atom:entry', ns)
    if entry is None:
        print("No entry found for this arxiv ID.")
        sys.exit(1)
    
    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
    authors = ', '.join(
        author.find('atom:name', ns).text
        for author in entry.findall('atom:author', ns)
    )
    published = entry.find('atom:published', ns).text
    year = int(published[:4])
    doi_elem = entry.find('arxiv:doi', ns)
    doi = doi_elem.text if doi_elem is not None else arxiv_id
    journal_elem = entry.find('arxiv:journal_ref', ns)
    journal = journal_elem.text if journal_elem is not None else "arXiv"
    
    return {
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "doi": doi,
        "link": f"https://arxiv.org/abs/{arxiv_id}"
    }
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage bibliography references.")
    subparsers = parser.add_subparsers(dest="command")

    # Add from arxiv
    add_arxiv_parser = subparsers.add_parser("add-arxiv", help="Add a reference from an arxiv URL.")
    add_arxiv_parser.add_argument("arxiv_url", help="The arxiv URL (e.g. https://arxiv.org/abs/2301.00001)")
    add_arxiv_parser.add_argument("--category", help="Category for the reference", required=False)
    add_arxiv_parser.add_argument("--file", default="references.csv", help="CSV file path")

    # Add manually
    add_parser = subparsers.add_parser("add", help="Add a reference manually.")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--authors", required=True)
    add_parser.add_argument("--journal", required=True)
    add_parser.add_argument("--year", required=True, type=int)
    add_parser.add_argument("--doi", required=True)
    add_parser.add_argument("--link", required=False)
    add_parser.add_argument("--category", required=False)
    add_parser.add_argument("--file", default="references.csv")

    # Generate markdown
    md_parser = subparsers.add_parser("markdown", help="Generate a markdown table from the CSV.")
    md_parser.add_argument("--file", default="references.csv")
    md_parser.add_argument("--by-category", action="store_true", help="Split tables by category")
    md_parser.add_argument("--output", default=None, help="Output file (e.g. README.md)")

    args = parser.parse_args()

    if args.command == "add-arxiv":
        arxiv_id = args.arxiv_url.split("/")[-1]
        metadata = fetch_arxiv_metadata(arxiv_id)
        category = args.category
        if category is None:
            category = input(f"Enter category for '{metadata['title']}': ")
        category = category.lower().strip()
        confirmed_input = input(f"Confirm adding '{metadata['title']}' to category '{category}'? (y/n): ")
        if not confirmed_input.lower() in ['y', 'yes', '']: # 'y', 'yes', or empty input (default to yes)
            print("Aborting.")
            sys.exit(0)
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
        print(f"Added: {metadata['title']}")

    elif args.command == "add":
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
        print(f"Added: {args.title}")

    elif args.command == "markdown":
        if args.by_category:
            table = make_markdown_tables_by_category(args.file)
        else:
            table = make_markdown_table(args.file)
        if args.output:
            with open(args.output, "w") as f:
                f.write(table)
            print(f"Markdown written to {args.output}")
        else:
            print(table)

    else:
        parser.print_help()