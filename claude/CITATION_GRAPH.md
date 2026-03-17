# Citation Graph Feature Documentation

## Overview

The citation graph feature builds an interactive visualization of how papers in your bibliography cite each other. It uses the Crossref API to query citation relationships and generates an interactive HTML graph using pyvis and networkx.

## Features

- **Citation Network Building**: Loads papers from CSV and queries Crossref API for their references
- **Directed Graph**: Creates a directed graph where edges represent citations (A → B means A cites B)
- **Interactive Visualization**: Generated HTML files allow zooming, panning, and dragging nodes
- **Physics Simulation**: Uses Barnes-Hut algorithm for natural graph layout
- **Metadata Support**: Nodes display paper titles, DOIs, authors, and years on hover

## Module Structure

### `graph.py`

Located in `pkg/mybib/graph.py`, this module provides core citation graph functionality:

#### `query_crossref_references(doi: str, max_retries: int = 3) -> list[str]`
- Queries the Crossref API for papers referenced by a given DOI
- Handles network errors with exponential backoff retry logic
- Returns a list of DOIs cited by the paper

#### `build_citation_graph(df: pd.DataFrame, output_references: bool = False) -> nx.DiGraph`
- Builds a directed graph from a DataFrame of references
- Adds all papers as nodes with metadata (title, authors, year, DOI)
- Queries Crossref API for each paper's references
- Adds edges only between papers that exist in your library
- Optional verbose output to track progress

#### `export_graph_html(graph: nx.DiGraph, output_file: str) -> None`
- Exports the citation graph as interactive HTML using pyvis
- Configures physics simulation for automatic layout
- Colors nodes in coral red (#FF6E63)
- Saves the visualization to specified output file

## Dependencies

Added to `pyproject.toml`:
- `networkx>=3.0` - Graph data structure and algorithms
- `pyvis>=0.3.2` - Interactive network visualization

## CLI Usage

### Command Syntax

```bash
mybib graph [options]
```

### Options

```
--file FILE              CSV file path (default: references.csv)
--output OUTPUT          Output HTML file (default: citation_graph.html)
--verbose                Print detailed progress information
```

### Examples

**Basic usage** (generates `citation_graph.html`):
```bash
mybib graph
```

**Custom output file**:
```bash
mybib graph --output my_citations.html
```

**Verbose output to monitor progress**:
```bash
mybib graph --verbose
```

**Custom references file**:
```bash
mybib graph --file my_papers.csv --output my_graph.html
```

## How It Works

1. **Load References**: Reads paper metadata from the CSV file
2. **Initialize Graph**: Creates an empty directed graph and adds all papers as nodes
3. **Query Cross​ref API**: For each paper:
   - Sends a request to `https://api.crossref.org/works/{DOI}`
   - Extracts all referenced DOIs
   - Adds edges from the paper to referenced papers (only if they're in your library)
   - Rate-limits requests (0.5s between requests)
4. **Generate Visualization**: Uses pyvis to create an interactive HTML visualization with:
   - Physics-based graph layout (Barnes-Hut algorithm)
   - Node labels showing truncated paper titles
   - Interactive zoom/pan/drag capabilities

## Performance Considerations

- **API Rate Limiting**: The tool adds a 0.5-second delay between Crossref API requests to be respectful
- **Network Timeout**: Set to 10 seconds per API request
- **Retry Logic**: Failed requests retry up to 3 times with exponential backoff

## Example Workflow

```python
from mybib.storage import load_references
from mybib.graph import build_citation_graph, export_graph_html

# Load your references
df = load_references("references.csv")

# Build the citation graph
graph = build_citation_graph(df, output_references=True)

# Export as interactive HTML
export_graph_html(graph, "my_citations.html")
```

Then open `my_citations.html` in your web browser to explore the citation network!

## Troubleshooting

### "Failed to query DOI" warnings
- This occurs when the Crossref API cannot find the paper
- Check that the DOI format is correct (should not include protocol prefix)
- The paper may not be indexed in Crossref yet

### No edges in the graph
- Edges are only created if both the citing paper and cited paper are in your library
- If your library is small, you may not see many edges
- This is intentional - it shows internal citation relationships only

### Graph takes a long time to generate
- This depends on the number of papers and network speed
- Each paper's references are queried individually with delays for politeness
- Expect ~1-2 seconds per paper

## Visual Interpretation

In the generated HTML visualization:
- **Nodes** (dots) represent papers in your library
- **Arrows** show citation direction (A → B means A cites B)
- **Node positioning** is determined by physics simulation:
  - Nodes repel each other (gravitational constant: -26000)
  - Edges act like springs pulling connected papers together
  - The system finds a natural, readable layout
- **Hover** over a node to see full paper details
- **Drag** nodes to reposition them
- **Scroll** to zoom in/out
- **Click and drag** on empty space to pan

## Files Added/Modified

- **Created**: `pkg/mybib/graph.py` - New module with graph functionality
- **Modified**: `pkg/mybib/cli.py` - Added `graph` subcommand and handler
- **Modified**: `pyproject.toml` - Added networkx and pyvis dependencies
