"""CSV storage for bibliography references."""

import pandas as pd
import sys
from pathlib import Path


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
    """Add a reference to the CSV file.
    
    Args:
        title: Article title
        authors: Comma-separated author names
        journal: Journal or publication name
        year: Publication year
        doi: DOI identifier
        link: URL link to the resource
        category: Category for classification
        file_path: Path to the CSV file
        
    Raises:
        SystemExit: If reference already exists
    """
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
    
    file_exists = Path(file_path).exists()
    
    if file_exists:
        existing_df = pd.read_csv(file_path)
        # Normalize DOI for comparison: convert to string, strip whitespace, lowercase
        existing_dois = set(
            str(d).strip().lower() 
            for d in existing_df["DOI"].to_list() 
            if pd.notna(d)
        )
        normalized_doi = str(doi).strip().lower()
        
        if normalized_doi in existing_dois:
            print("Reference already exists in the CSV file.")
            sys.exit(0)
    
    row.to_csv(file_path, mode="a", index=False, header=not file_exists)


def load_references(file_path: str = "references.csv") -> pd.DataFrame:
    """Load references from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with reference data
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(
            columns=["Title", "Authors", "Journal", "Year", "DOI", "Link", "Category"]
        )
        df.to_csv(file_path, index=False)
    
    return df