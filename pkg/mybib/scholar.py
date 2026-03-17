"""Fetch metadata from Google Scholar using SerpAPI."""

import sys
import os
import requests
import json
from typing import Optional, Dict, List
from urllib.parse import urlencode

# Suppress SSL warnings if needed
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass


def search_google_scholar(query: str, max_results: int = 5) -> List[Dict]:
    """Search Google Scholar for articles matching a query.
    
    Args:
        query: Search query (title, authors, or keywords)
        max_results: Maximum number of results to return (1-20)
        
    Returns:
        List of results with keys: position, title, result_id, link, snippet, 
        publication_info, inline_links, authors, year, etc.
        
    Raises:
        SystemExit: If API call fails or key is missing
    """
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("Error: SERPAPI_KEY environment variable not set.")
        print("Get a free API key at https://serpapi.com")
        sys.exit(1)
    
    params = {
        "engine": "google_scholar",
        "q": query,
        "api_key": api_key,
        "num": min(max_results, 20),
        "hl": "en",
    }
    
    url = "https://serpapi.com/search"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"Error from SerpAPI: {data['error']}")
            sys.exit(1)
        
        organic_results = data.get("organic_results", [])
        return organic_results
        
    except requests.exceptions.RequestException as e:
        print(f"Error querying Google Scholar: {e}")
        sys.exit(1)


def get_scholar_cite_link(result_id: str) -> Optional[str]:
    """Get the Google Scholar cite link for a result.
    
    Args:
        result_id: The result ID from search results
        
    Returns:
        The SerpAPI cite API link, or None if not available
    """
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        return None
    
    # Format: https://serpapi.com/search.json?engine=google_scholar_cite&q={result_id}&api_key={api_key}
    return f"https://serpapi.com/search.json?engine=google_scholar_cite&q={result_id}&api_key={api_key}"


def fetch_bibtex_from_scholar(result_id: str) -> Optional[str]:
    """Fetch BibTeX citation from Google Scholar using SerpAPI cite API.
    
    Args:
        result_id: The result ID from a Google Scholar search result
        
    Returns:
        BibTeX string, or None if unable to fetch
    """
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("Error: SERPAPI_KEY environment variable not set.")
        return None
    
    params = {
        "engine": "google_scholar_cite",
        "q": result_id,
        "api_key": api_key,
    }
    
    url = "https://serpapi.com/search"
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"Error from SerpAPI: {data['error']}")
            return None
        
        # SerpAPI returns citations in different formats
        # The BibTeX is typically in the response as a string or in a structured format
        citations = data.get("citations", {})
        
        # Try to find BibTeX format
        bibtex = citations.get("bibtex")
        if bibtex:
            return bibtex
        
        # If we can't find BibTeX, we might need to construct it from available data
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching BibTeX from Google Scholar: {e}")
        return None


def extract_metadata_from_result(result: Dict) -> Dict:
    """Extract standardized metadata from a Google Scholar search result.
    
    Args:
        result: A single result from search_google_scholar()
        
    Returns:
        Dictionary with keys: title, authors, journal, year, doi, link, scholar_id
    """
    import re
    
    metadata = {
        "title": result.get("title", ""),
        "authors": "",
        "journal": "",
        "year": None,
        "doi": None,
        "link": result.get("link", ""),
        "result_id": result.get("result_id", ""),
        "scholar_id": result.get("result_id", ""),
    }
    
    # Extract publication info
    pub_info = result.get("publication_info", {})
    if isinstance(pub_info, dict):
        summary = pub_info.get("summary", "")
        metadata["journal"] = summary
        
        # Try to extract year from summary - look for 4-digit years (1900-2099)
        # Use a more specific pattern to avoid partial matches
        year_matches = re.findall(r'\b(19\d{2}|20\d{2})\b', summary)
        if year_matches:
            # Take the most likely year (prefer 20xx over 19xx if available)
            for year_str in year_matches:
                metadata["year"] = int(year_str)
                # Prefer years starting with 20
                if year_str.startswith('20'):
                    break
        
        # Try to extract DOI from summary (pattern: 10.xxxx/xxxx)
        doi_match = re.search(r'\b(10\.\S+/\S+)\b', summary)
        if doi_match:
            metadata["doi"] = doi_match.group(1)
        
        # Extract authors
        authors_list = pub_info.get("authors", [])
        if authors_list:
            if isinstance(authors_list, list):
                author_names = []
                for author in authors_list:
                    if isinstance(author, dict):
                        author_names.append(author.get("name", ""))
                    else:
                        author_names.append(str(author))
                metadata["authors"] = ", ".join(author_names)
            else:
                metadata["authors"] = str(authors_list)
    
    # Try to extract year from other fields if not found
    if metadata["year"] is None:
        title_year_match = re.search(r'\((\d{4})\)', metadata["title"])
        if title_year_match:
            metadata["year"] = int(title_year_match.group(1))
    
    # Try to extract DOI from result directly if not found in summary
    if metadata["doi"] is None:
        if "doi" in result:
            metadata["doi"] = result.get("doi")
        elif "inline_links" in result:
            inline_links = result["inline_links"]
            if isinstance(inline_links, dict):
                # Check for DOI link in inline_links
                for key, value in inline_links.items():
                    if "doi.org" in str(value):
                        doi_match = re.search(r'doi\.org/(.+?)(?:\s|$)', str(value))
                        if doi_match:
                            metadata["doi"] = doi_match.group(1)
                            break
    
    # Note: We do NOT use scholar_id as a fallback for DOI because they are different identifiers.
    # Scholar ID is Google Scholar's internal identifier, not a DOI.
    # If no real DOI is found, leave it as None.
    
    return metadata


def search_and_confirm_article(title: str, max_attempts: int = 3) -> Optional[Dict]:
    """Search for an article on Google Scholar and get user confirmation.
    
    Args:
        title: Article title to search for
        max_attempts: Maximum attempts to find a match
        
    Returns:
        Metadata dictionary if found and confirmed, None otherwise
    """
    from .ui import console, confirm_action, display_reference_preview
    
    console.print(f"[cyan]Searching Google Scholar for: {title}[/]")
    
    results = search_google_scholar(title, max_results=5)
    
    if not results:
        console.print("[red]No results found on Google Scholar[/]")
        return None
    
    # Show first result and ask for confirmation
    first_result = results[0]
    metadata = extract_metadata_from_result(first_result)
    
    console.print()
    console.print("[yellow]Found:[/]")
    display_reference_preview(metadata)
    console.print()
    
    if confirm_action("Is this the correct article?"):
        return metadata
    
    # If not confirmed, show other results
    if len(results) > 1:
        for i, result in enumerate(results[1:], 1):
            console.print()
            console.print(f"[yellow]Option {i + 1}:[/]")
            result_metadata = extract_metadata_from_result(result)
            display_reference_preview(result_metadata)
            console.print()
            
            if confirm_action(f"Is this the correct article?"):
                return result_metadata
            
            if i >= max_attempts - 1:
                break
    
    console.print("[red]No matching article confirmed[/]")
    return None
