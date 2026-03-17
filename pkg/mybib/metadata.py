"""Fetch metadata from multiple sources (arXiv, DOI, or generic URLs)."""

import re
import sys
import requests
from urllib.parse import urlparse

from . import arxiv


def fetch_metadata(url: str) -> dict:
    """Fetch metadata from a URL, automatically detecting the source.
    
    Supports:
    - arXiv URLs (arxiv.org)
    - DOI URLs (doi.org) and DOI patterns
    - Generic URLs with HTML metadata extraction
    
    Args:
        url: URL or DOI string to fetch metadata from
        
    Returns:
        Dictionary with standardized fields:
        {
            'title': str,
            'authors': str,
            'journal': str,
            'year': int or None,
            'doi': str or None,
            'link': str
        }
        
    Raises:
        SystemExit: If URL is invalid or metadata cannot be extracted
    """
    url = url.strip()
    
    # Detect source and route to appropriate handler
    if _is_arxiv_url(url):
        return _fetch_arxiv_metadata(url)
    elif _is_doi_url(url) or _is_doi_pattern(url):
        return _fetch_crossref_metadata(url)
    else:
        return _fetch_generic_metadata(url)


def _is_arxiv_url(url: str) -> bool:
    """Check if URL is from arxiv.org."""
    return "arxiv.org" in url.lower()


def _is_doi_url(url: str) -> bool:
    """Check if URL is a DOI URL (doi.org)."""
    return "doi.org" in url.lower()


def _is_doi_pattern(url: str) -> bool:
    """Check if string matches DOI pattern (e.g., 10.xxxx/xxxx)."""
    # DOI pattern: 10. followed by number/symbol, then slash, then alphanumeric
    return bool(re.match(r"^10\.\S+/\S+", url))


def _extract_arxiv_id(url: str) -> str:
    """Extract arXiv ID from URL.
    
    Examples:
    - https://arxiv.org/abs/2301.00001 -> 2301.00001
    - https://arxiv.org/pdf/2301.00001.pdf -> 2301.00001
    """
    # Match patterns like: /abs/2301.00001 or /pdf/2301.00001
    match = re.search(r"/(?:abs|pdf)/(\d{4}\.\d{4,5})", url)
    if match:
        return match.group(1)
    
    print(f"Error: Could not extract arXiv ID from {url}")
    sys.exit(1)


def _fetch_arxiv_metadata(url: str) -> dict:
    """Fetch metadata from arXiv using the arXiv API."""
    arxiv_id = _extract_arxiv_id(url)
    return arxiv.fetch_arxiv_metadata(arxiv_id)


def _normalize_doi(url_or_doi: str) -> str:
    """Extract DOI from URL or return as-is if already a DOI."""
    if "doi.org/" in url_or_doi.lower():
        # Extract DOI from URL: https://doi.org/10.xxxx/xxxx
        match = re.search(r"doi\.org/(.+)$", url_or_doi, re.IGNORECASE)
        if match:
            return match.group(1)
    return url_or_doi


def _fetch_crossref_metadata(url_or_doi: str) -> dict:
    """Fetch metadata from Crossref API using DOI."""
    doi = _normalize_doi(url_or_doi)
    
    # Crossref API endpoint
    crossref_url = f"https://api.crossref.org/works/{doi}"
    
    try:
        response = requests.get(crossref_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching DOI metadata: {e}")
        sys.exit(1)
    
    data = response.json()
    if data.get("status") != "ok" or not data.get("message"):
        print(f"Error: Could not fetch metadata for DOI {doi}")
        sys.exit(1)
    
    work = data["message"]
    
    # Extract fields with fallbacks
    title = work.get("title", [""])[0] if isinstance(work.get("title"), list) else work.get("title", "Unknown")
    
    # Authors
    authors = ""
    if "author" in work:
        author_list = [
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in work["author"]
        ]
        authors = ", ".join(author_list)
    
    # Journal
    journal = work.get("container-title", "Unknown")
    if isinstance(journal, list):
        journal = journal[0] if journal else "Unknown"
    
    # Year
    year = None
    if "issued" in work:
        date_parts = work["issued"].get("date-parts", [[None]])[0]
        if date_parts:
            year = date_parts[0]
    
    # Link (prefer DOI link, fallback to URL)
    link = work.get("URL", f"https://doi.org/{doi}")
    
    return {
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "doi": doi,
        "link": link
    }


def _fetch_generic_metadata(url: str) -> dict:
    """Fetch metadata from generic URL using HTML meta tags parsing."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)
    
    html = response.text
    
    # Extract title from <title> tag or og:title meta tag
    title = _extract_html_meta(html, ["og:title", "twitter:title"])
    if not title:
        title_match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Unknown"
    
    # Extract author
    authors = _extract_html_meta(html, ["author", "article:author"])
    
    # Try to extract DOI
    doi = None
    doi_match = re.search(r"10\.\S+/\S+", html)
    if doi_match:
        doi = doi_match.group(0)
    
    return {
        "title": title or "Unknown",
        "authors": authors or "Unknown",
        "journal": "Unknown",
        "year": None,
        "doi": doi,
        "link": url
    }


def _extract_html_meta(html: str, meta_names: list) -> str:
    """Extract value from HTML meta tags.
    
    Args:
        html: HTML content as string
        meta_names: List of meta tag names to search for
        
    Returns:
        Content of the first matching meta tag, or None if not found
    """
    for meta_name in meta_names:
        # Try property attribute (og:*, twitter:*, etc.)
        pattern = rf'<meta\s+property="{re.escape(meta_name)}"\s+content="([^"]*)"'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try name attribute
        pattern = rf'<meta\s+name="{re.escape(meta_name)}"\s+content="([^"]*)"'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try reverse order (content first)
        pattern = rf'<meta\s+content="([^"]*)"\s+(?:property|name)="{re.escape(meta_name)}"'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None
