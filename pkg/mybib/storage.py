"""CSV storage for bibliography references."""

import hashlib
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
    bibtex: str = None,
    bibtex_dir: str = "bibtex_entries",
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
        bibtex: Raw BibTeX entry (optional)
        bibtex_dir: Directory where BibTeX files are stored
        file_path: Path to the CSV file

    Raises:
        SystemExit: If reference already exists
    """
    # Use scholar_id as DOI fallback if DOI not provided
    final_doi = doi if doi else scholar_id

    bibtex_path = _store_bibtex_entry(
        bibtex=bibtex,
        doi=final_doi,
        title=title,
        csv_file_path=file_path,
        bibtex_dir=bibtex_dir,
    )

    new_reference = {
        "Title": title,
        "Authors": authors,
        "Journal": journal,
        "Year": year,
        "DOI": final_doi,
        "Link": link,
        "Category": category,
        "ArxivID": arxiv_id or "",
        "BibTeX": "",
        "BibTeXPath": bibtex_path or "",
    }
    row = pd.DataFrame([new_reference])

    file_exists = Path(file_path).exists()

    if file_exists:
        df_existing = pd.read_csv(file_path)
        changed = False
        if "ArxivID" not in df_existing.columns:
            df_existing["ArxivID"] = ""
            changed = True
        if "BibTeX" not in df_existing.columns:
            df_existing["BibTeX"] = ""
            changed = True
        if "BibTeXPath" not in df_existing.columns:
            df_existing["BibTeXPath"] = ""
            changed = True
        if changed:
            df_existing.to_csv(file_path, index=False)

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

        if "BibTeX" in df.columns:
            df["BibTeX"] = df["BibTeX"].fillna("").replace(["nan", "<NA>"], "")
        else:
            df["BibTeX"] = ""
            df.to_csv(file_path, index=False)

        if "BibTeXPath" in df.columns:
            df["BibTeXPath"] = (
                df["BibTeXPath"].fillna("").replace(["nan", "<NA>"], "")
            )
        else:
            df["BibTeXPath"] = ""
            df.to_csv(file_path, index=False)
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
                "BibTeX",
                "BibTeXPath",
            ]
        )
        df = df.astype({"ArxivID": str})
        df.to_csv(file_path, index=False)

    return df


def store_bibtex_for_existing_row(
    bibtex: str,
    doi: str,
    title: str,
    csv_file_path: str,
    bibtex_dir: str = "bibtex_entries",
) -> str | None:
    """Store BibTeX for an existing row and return relative path."""
    return _store_bibtex_entry(
        bibtex=bibtex,
        doi=doi,
        title=title,
        csv_file_path=csv_file_path,
        bibtex_dir=bibtex_dir,
    )


def _store_bibtex_entry(
    bibtex: str,
    doi: str,
    title: str,
    csv_file_path: str,
    bibtex_dir: str,
) -> str | None:
    """Persist BibTeX in a file and return path relative to CSV directory."""
    text = "" if bibtex is None else str(bibtex).strip()
    if not text or text.lower() == "nan" or not text.startswith("@"):
        return None

    csv_parent = Path(csv_file_path).resolve().parent
    output_dir = csv_parent / bibtex_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    file_stem = _make_bibtex_file_stem(doi=doi, title=title)
    output_path = output_dir / f"{file_stem}.bib"
    output_path.write_text(text + "\n", encoding="utf-8")

    return str(output_path.relative_to(csv_parent))


def _make_bibtex_file_stem(doi: str, title: str) -> str:
    """Create stable file-name stem for BibTeX entries."""
    source = str(doi).strip() if doi else str(title).strip()
    lowered = source.lower()
    sanitized = "".join(ch if ch.isalnum() else "_" for ch in lowered)
    compact = "_".join(part for part in sanitized.split("_") if part)
    compact = compact[:80] if compact else "entry"

    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:8]
    return f"{compact}_{digest}"
