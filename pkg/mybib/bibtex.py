"""Generate BibTeX files from reference data."""

import pandas as pd


def generate_bibtex(df: pd.DataFrame) -> str:
    """Generate BibTeX entries from a DataFrame of references.
    
    Args:
        df: DataFrame with columns: Title, Authors, Journal, Year, DOI, Link
        
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
        if col_lower == 'title':
            col_mapping['title'] = col
        elif col_lower == 'authors':
            col_mapping['authors'] = col
        elif col_lower == 'journal':
            col_mapping['journal'] = col
        elif col_lower == 'year':
            col_mapping['year'] = col
        elif col_lower == 'doi':
            col_mapping['doi'] = col
        elif col_lower == 'link':
            col_mapping['link'] = col
        elif col_lower == 'url':
            col_mapping['link'] = col
    
    entries = []
    
    for _, row in df.iterrows():
        # Extract values using mapped column names
        title = str(row.get(col_mapping.get('title', 'Title'), "")).strip()
        authors = str(row.get(col_mapping.get('authors', 'Authors'), "")).strip()
        journal = str(row.get(col_mapping.get('journal', 'Journal'), "")).strip()
        year = str(row.get(col_mapping.get('year', 'Year'), "")).strip()
        doi = str(row.get(col_mapping.get('doi', 'DOI'), "")).strip()
        link = str(row.get(col_mapping.get('link', 'Link'), "")).strip()
        
        # Skip entries with missing critical fields
        if not title:
            continue
        
        # Use DOI as the key, or create one from title if DOI is missing
        if doi and doi != "nan":
            key = doi
        else:
            # Fallback: create key from title
            key = title.lower().replace(" ", "_").replace(":", "")[:30]
        
        # Build BibTeX entry
        entry = f"@article{{{key},\n"
        entry += f'  title={{{title}}},\n'
        
        if authors:
            entry += f'  author={{{authors}}},\n'
        if journal:
            entry += f'  journal={{{journal}}},\n'
        if year and year != "nan":
            entry += f'  year={{{year}}},\n'
        if link and link != "nan":
            entry += f'  url={{{link}}}\n'
        
        entry += "}\n"
        
        entries.append(entry)
    
    return "\n".join(entries)

