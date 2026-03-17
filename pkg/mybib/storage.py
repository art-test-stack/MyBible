"""CSV storage for bibliography references."""

import sys
from pathlib import Path

import pandas as pd


def add_reference(
    title: str,
    authors: str,
    journal: str,
    year: int,
    doi: str,
    link: str,
    category: str,
    arxiv_id: str = None,
    scholar_id: str = None,
    file_path: str = "references.csv",
) -> None:
    """Add a reference to the CSV file.

    Args:
        title: Article title
        authors: Comma-separated author names
        journal: Journal or publication name
        year: Publication year
        doi: DOI identifier (uses scholar_id as fallback if not provided)
        link: URL link to the resource
        category: Category for classification
        arxiv_id: arXiv identifier (optional)
        scholar_id: Google Scholar result ID (optional, used as DOI fallback)
        file_path: Path to the CSV file

    Raises:
        SystemExit: If reference already exists
    """
    # Use scholar_id as DOI fallback if DOI not provided
    final_doi = doi if doi else scholar_id

    new_reference = {
        "Title": title,
        "Authors": authors,
        "Journal": journal,
        "Year": year,
        "DOI": final_doi,
        "Link": link,
        "Category": category,
        "ArxivID": arxiv_id or "",
    }
    row = pd.DataFrame([new_reference])

    file_exists = Path(file_path).exists()

    if file_exists:
        df_existing = pd.read_csv(file_path)
        # Convert ArxivID to string for comparison
        if "ArxivID" in df_existing.columns:
            df_existing["ArxivID"] = df_existing["ArxivID"].astype(str)
        existing_df = df_existing
        # Normalize DOI for comparison: convert to string, strip whitespace, lowercase
        existing_dois = set(
            str(d).strip().lower() for d in existing_df["DOI"].to_list() if pd.notna(d)
        )
        normalized_doi = str(final_doi).strip().lower() if final_doi else ""

        if normalized_doi and normalized_doi in existing_dois:
            print("Reference already exists in the CSV file.")
            sys.exit(0)

    # Ensure ArxivID is treated as string
    row["ArxivID"] = row["ArxivID"].astype(str)
    row.to_csv(file_path, mode="a", index=False, header=not file_exists)


def load_references(file_path: str = "references.csv") -> pd.DataFrame:
    """Load references from CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame with reference data
    """
    try:
        # Read with ArxivID as string to prevent numeric conversion
        df = pd.read_csv(file_path, dtype={"ArxivID": str})
        # Replace NaN strings with empty strings
        if "ArxivID" in df.columns:
            df["ArxivID"] = df["ArxivID"].fillna("").replace(["nan", "<NA>"], "")
        else:
            df["ArxivID"] = ""
    except FileNotFoundError:
        df = pd.DataFrame(
            columns=[
                "Title",
                "Authors",
                "Journal",
                "Year",
                "DOI",
                "Link",
                "Category",
                "ArxivID",
            ]
        )
        df = df.astype({"ArxivID": str})
        df.to_csv(file_path, index=False)

    return df
