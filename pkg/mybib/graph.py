"""Citation graph building and visualization using Crossref API."""

import time

import networkx as nx
import pandas as pd
import requests


def query_crossref_references(doi: str, max_retries: int = 3) -> list[str]:
    """Query Crossref API for references cited by a given DOI.

    Args:
        doi: The DOI of the paper to query (e.g., "10.1234/example")
        max_retries: Maximum number of retry attempts

    Returns:
        List of DOIs cited by the paper
    """
    # Ensure DOI doesn't have 'https://doi.org/' prefix
    doi_clean = doi.strip().lstrip("https://doi.org/").lstrip("http://doi.org/")

    url = f"https://api.crossref.org/works/{doi_clean}"
    headers = {"User-Agent": "MyBible (mailto:test@example.com)"}

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "ok":
                work = data.get("message", {})
                references = work.get("reference", [])

                # Extract DOIs from references
                reference_dois = []
                for ref in references:
                    if isinstance(ref, dict) and "DOI" in ref:
                        reference_dois.append(ref["DOI"].lower())

                return reference_dois

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2**attempt
                time.sleep(wait_time)
            else:
                print(f"Warning: Failed to query DOI {doi_clean}: {e}")

    return []


def build_citation_graph(
    df: pd.DataFrame, output_references: bool = False
) -> nx.DiGraph:
    """Build a citation graph from stored research papers.

    Creates a directed graph where:
    - Nodes represent papers (identified by DOI)
    - Edges represent citations (paper A -> paper B means A cites B)

    Args:
        df: DataFrame with columns including 'DOI' and 'Title'
        output_references: If True, print progress information

    Returns:
        A NetworkX directed graph
    """
    graph = nx.DiGraph()

    # Add all papers as nodes
    paper_dois = {}  # Maps clean DOI to original DOI
    for idx, row in df.iterrows():
        doi = str(row["DOI"]).strip()
        if not doi or doi.lower() == "nan":
            continue

        # Normalize DOI for use as node identifier
        doi_clean = doi.lstrip("https://doi.org/").lstrip("http://doi.org/").lower()
        paper_dois[doi_clean] = doi

        title = row.get("Title", "Unknown")
        graph.add_node(
            doi_clean,
            title=title,
            original_doi=doi,
            authors=row.get("Authors", ""),
            year=row.get("Year", ""),
        )

    if output_references:
        print(f"Added {len(graph.nodes())} papers to graph")

    # Query Crossref API for each paper's references
    stored_dois = set(paper_dois.keys())

    for idx, (doi_clean, doi_original) in enumerate(paper_dois.items()):
        if output_references:
            print(
                f"Querying references for paper "
                f"{idx + 1}/{len(paper_dois)}: {doi_clean}"
            )

        # Query Crossref for references
        reference_dois = query_crossref_references(doi_original)

        # Add edges only for references in our stored papers
        for ref_doi in reference_dois:
            if ref_doi in stored_dois:
                # Edge direction: doi_clean -> ref_doi (paper cites reference)
                graph.add_edge(doi_clean, ref_doi)
                if output_references:
                    print(f"  -> Edge: {doi_clean} cites {ref_doi}")

        # Rate limiting: Crossref API recommends polite usage
        time.sleep(0.5)

    if output_references:
        print(
            f"Citation graph built with {len(graph.nodes())} nodes "
            f"and {len(graph.edges())} edges"
        )

    return graph


def export_graph_html(graph: nx.DiGraph, output_file: str) -> None:
    """Export citation graph as interactive HTML using pyvis.

    Args:
        graph: NetworkX directed graph
        output_file: Path to output HTML file
    """
    try:
        from pyvis.network import Network
    except ImportError:
        raise ImportError(
            "pyvis is required for graph visualization. "
            "Install it with: pip install pyvis"
        )

    import json

    # Create pyvis network
    net = Network(directed=True, height="750px", width="100%")

    # Add nodes with labels
    for node in graph.nodes(data=True):
        node_id = node[0]
        node_data = node[1]

        title = node_data.get("title", "Unknown")
        label = title[:50] + "..." if len(title) > 50 else title

        # Create hover title with full information
        hover_title = f"{title}\nDOI: {node_data.get('original_doi', '')}"

        net.add_node(node_id, label=label, title=hover_title, color="#FF6E63")

    # Add edges
    for edge in graph.edges():
        source, target = edge
        net.add_edge(source, target)

    # Configure physics settings as JSON string
    options = {
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -26000,
                "centralGravity": 0.3,
                "springLength": 200,
                "springConstant": 0.04,
            },
        }
    }
    net.set_options(json.dumps(options))

    # Write HTML file
    net.write_html(output_file)
    print(f"Citation graph exported to {output_file}")
