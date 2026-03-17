"""Fetch metadata from arXiv API."""

import sys
import requests
import xml.etree.ElementTree as ET


def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    """Fetch metadata from arXiv API.
    
    Args:
        arxiv_id: arXiv identifier (e.g., '2301.00001')
        
    Returns:
        Dictionary with keys: title, authors, journal, year, doi, link
        
    Raises:
        SystemExit: If API call fails or no entry found
    """
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
