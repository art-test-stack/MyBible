"""Generate BibTeX files from reference data."""

from pathlib import Path

import pandas as pd


def generate_bibtex(df: pd.DataFrame, csv_file: str = "references.csv") -> str:
    """Generate BibTeX entries from a DataFrame of references.

    Args:
        df: DataFrame with columns: Title, Authors, Journal, Year, DOI, Link
        csv_file: Source CSV path used to resolve relative BibTeX file paths

    Returns:
        String containing BibTeX formatted entries
    """
    if df.empty:
        return "% No references found\n"

    # Handle cases where DataFrame column names might not exactly match
    # Create a mapping of expected columns to actual columns
    col_mapping = {}

    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower == "title":
            col_mapping["title"] = col
        elif col_lower == "authors":
            col_mapping["authors"] = col
        elif col_lower == "journal":
            col_mapping["journal"] = col
        elif col_lower == "year":
            col_mapping["year"] = col
        elif col_lower == "doi":
            col_mapping["doi"] = col
        elif col_lower == "link":
            col_mapping["link"] = col
        elif col_lower == "url":
            col_mapping["link"] = col
        elif col_lower in {"bibtex", "bibtexentry"}:
            col_mapping["bibtex"] = col
        elif col_lower in {"bibtexpath", "bib_path"}:
            col_mapping["bibtex_path"] = col

    entries = []

    for _, row in df.iterrows():
        # Extract values using mapped column names
        title = str(row.get(col_mapping.get("title", "Title"), "")).strip()
        authors = str(row.get(col_mapping.get("authors", "Authors"), "")).strip()
        journal = str(row.get(col_mapping.get("journal", "Journal"), "")).strip()
        year = str(row.get(col_mapping.get("year", "Year"), "")).strip()
        doi = str(row.get(col_mapping.get("doi", "DOI"), "")).strip()
        link = str(row.get(col_mapping.get("link", "Link"), "")).strip()
        raw_bibtex = str(row.get(col_mapping.get("bibtex", "BibTeX"), "")).strip()
        bibtex_path = str(
            row.get(col_mapping.get("bibtex_path", "BibTeXPath"), "")
        ).strip()

        # Skip entries with missing critical fields
        if not title:
            continue

        file_bibtex = _read_bibtex_from_path(csv_file=csv_file, bibtex_path=bibtex_path)
        if file_bibtex:
            entries.append(file_bibtex)
            continue

        # Prefer citation BibTeX fetched from source when available
        if raw_bibtex and raw_bibtex.lower() != "nan" and raw_bibtex.startswith("@"):
            entries.append(raw_bibtex)
            continue

        # Use DOI as the key, or create one from title if DOI is missing
        if doi and doi != "nan":
            key = doi
        else:
            # Fallback: create key from title
            key = title.lower().replace(" ", "_").replace(":", "")[:30]

        # Build BibTeX entry
        entry = f"@article{{{key},\n"
        entry += f"  title={{{title}}},\n"

        if authors:
            entry += f"  author={{{authors}}},\n"
        if journal:
            entry += f"  journal={{{journal}}},\n"
        if year and year != "nan":
            entry += f"  year={{{year}}},\n"
        if link and link != "nan":
            entry += f"  url={{{link}}}\n"

        entry += "}\n"

        entries.append(entry)

    return "\n\n".join(entries)


def _read_bibtex_from_path(csv_file: str, bibtex_path: str) -> str | None:
    """Read BibTeX content from a relative or absolute file path."""
    if not bibtex_path or bibtex_path.lower() == "nan":
        return None

    candidate = Path(bibtex_path)
    if not candidate.is_absolute():
        candidate = Path(csv_file).resolve().parent / candidate

    if not candidate.exists():
        return None

    content = candidate.read_text(encoding="utf-8").strip()
    if content.startswith("@"):
        return content

    return None
