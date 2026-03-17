# 📚 MyBible - Research Paper Bibliography Manager

A modern, feature-rich CLI tool for managing a curated collection of research papers with beautiful terminal output, interactive visualizations, and comprehensive testing.

## Overview

MyBible is a comprehensive bibliography management system designed to help researchers organize, track, and analyze their research paper collections. This repository contains a curated list of important research papers (primarily from AI research) with tools to:

- ✨ **Add papers** from arXiv or manually with beautiful CLI prompts
- 📊 **Generate markdown tables** for easy navigation and sharing
- 📖 **Export to BibTeX** for use in LaTeX documents
- 🕸️ **Visualize citation networks** with interactive HTML graphs
- ✅ **Track duplicates** with intelligent detection
- 🧪 **Comprehensive test coverage** for reliability

The papers are organized into categories based on their topics, with each entry including title, authors, journal, publication year, and DOI links for easy access.

## Quick Start

### Installation

```bash
# Clone and set up the environment
git clone <repository-url>
cd MyBible
uv sync
```

### Adding Papers

#### From arXiv
```bash
uv run mybib add-arxiv <arxiv_url> --category <category_name>
```

Example:
```bash
uv run mybib add-arxiv https://arxiv.org/abs/2401.00001 --category "LLMs Basics"
```

#### Manual Entry
```bash
uv run mybib add --title "<title>" --authors "<author1>, <author2>, ..." \
  --journal "<journal>" --year <year> --doi "<doi>" --category <category>
```

### Generating Output

#### Markdown Tables
```bash
uv run mybib markdown --file references.csv --output references.md
```

#### BibTeX Export
```bash
uv run mybib bibtex --file references.csv --output references.bib
```

#### Citation Network Graph
```bash
uv run mybib graph --file references.csv --output citation_graph.html
```

## Features

### 🎨 Modern CLI User Experience

All commands feature:
- **Colored output**: Success (✓), error (✗), warning (⚠), and info (ℹ) messages
- **Progress indicators**: Smooth animations when fetching from APIs
- **Confirmation prompts**: Safe defaults for destructive actions
- **Beautiful tables**: Rich formatting for better readability

Example of adding a paper:
```
Title: Attention is all you need
Authors: Vaswani et al.
Journal: NeurIPS
Year: 2017
DOI: 10.1038/nature12373

Add 'Attention is all you need' to category 'LLMs Basics'? [y/N]: y
✓ Reference added successfully to category 'LLMs Basics'
```

### 📊 Markdown Table Generation

Automatically generate organized markdown tables from your bibliography:
- Tables organized by category
- Columns: Title, Authors, Journal, Year, DOI
- Clickable DOI links
- Proper author name formatting (et al. for 3+ authors)
- Sorted by category and publication year

### 📖 BibTeX Export

Generate standard BibTeX files for LaTeX documents with properly formatted entries including:
- Author names
- Publication title
- Journal/Venue
- Publication year
- DOI formatting

### 🕸️ Citation Network Visualization

Build interactive citation graphs showing how papers in your library cite each other:
- **Network building**: Queries Crossref API for citation relationships
- **Interactive visualization**: Zoom, pan, and drag nodes
- **Physics simulation**: Automatic layout using Barnes-Hut algorithm
- **Metadata on hover**: View paper details without clicking

**Features:**
- Directed graph representation (A → B means A cites B)
- Only includes edges between papers in your library
- Color-coded visualization
- Handles network errors gracefully with retry logic

**Usage:**
```bash
# Generate citation graph with verbose output
mybib graph --file references.csv --output my_citations.html --verbose
```

### ✅ Duplicate Detection

Built-in duplicate detection when adding new papers:
- DOI-based matching
- Case-insensitive comparison
- Whitespace normalization
- Prevents accidental duplicates in your bibliography

### 🧪 Comprehensive Test Suite

The project includes extensive pytest tests covering:

**Storage Module** (`test_storage.py`):
- Adding references to CSV files
- Duplicate detection with various formats
- Loading and preserving reference data

**ArXiv Module** (`test_arxiv.py`):
- Metadata fetching from arXiv API
- Multiple author parsing
- Error handling and fallbacks
- URL formation and validation

**Markdown Module** (`test_markdown.py`):
- Table generation with various formats
- Category-based organization
- Author name reformatting
- Sorting and filtering

**Running Tests:**
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_storage.py -v

# Run with coverage
python -m pytest tests/ --cov=pkg/mybib
```

## Architecture

### Project Structure

```
MyBible/
├── pkg/mybib/              # Main package
│   ├── __init__.py
│   ├── cli.py              # CLI command handlers
│   ├── storage.py          # CSV storage operations
│   ├── arxiv.py            # arXiv API integration
│   ├── metadata.py         # Metadata management
│   ├── markdown.py         # Markdown generation
│   ├── bibtex.py           # BibTeX export
│   ├── graph.py            # Citation graph features
│   ├── ui.py               # Terminal UI utilities
│   └── utils.py            # Utility functions
├── tests/                  # Test suite
│   ├── test_storage.py
│   ├── test_arxiv.py
│   ├── test_markdown.py
│   └── test_metadata.py
├── references.csv          # Bibliography database
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

### Core Modules

- **`cli.py`**: Command-line interface with rich formatting
- **`storage.py`**: CSV file handling and duplicate detection
- **`arxiv.py`**: arXiv metadata fetching with error handling
- **`metadata.py`**: Reference metadata management
- **`markdown.py`**: Markdown table generation with category support
- **`bibtex.py`**: BibTeX export functionality
- **`graph.py`**: Citation network building and visualization
- **`ui.py`**: Terminal UI components (colors, progress, confirmations)

## Dependencies

Core dependencies (installed via `uv sync`):
- `pandas`: CSV data handling
- `requests`: HTTP requests for APIs
- `rich`: Beautiful terminal output
- `networkx`: Graph algorithms and data structures
- `pyvis`: Interactive network visualization

Development dependencies:
- `pytest`: Testing framework
- `pytest-cov`: Code coverage reporting

## CLI Commands

```bash
# View help
mybib --help
mybib add-arxiv --help
mybib add --help
mybib markdown --help
mybib bibtex --help
mybib graph --help

# Add from arXiv
mybib add-arxiv <arxiv_url> --category <category>

# Add manually
mybib add --title "<title>" --authors "<authors>" --journal "<journal>" \
  --year <year> --doi "<doi>" --category <category>

# Generate markdown
mybib markdown [--file references.csv] [--output references.md]

# Generate BibTeX
mybib bibtex [--file references.csv] [--output references.bib]

# Generate citation graph
mybib graph [--file references.csv] [--output citation_graph.html] [--verbose]
```

## Data Format

References are stored in `references.csv` with the following columns:
- **Title**: Paper title
- **Authors**: Author names (comma-separated)
- **Journal**: Publication venue
- **Year**: Publication year
- **DOI**: Digital Object Identifier
- **Category**: Research topic category
- **Link**: URL (optional)

## Future Enhancements

Potential features for future versions:
- Paper summaries and key insights
- Personal reading notes and annotations
- Reading progress tracking (read/unread status)
- Topic clustering visualization
- Advanced search and filtering
- Export to other formats (RIS, Zotero)
- Integration with reference managers
- Automated paper recommendation based on citations

## Contributing

Contributions are welcome! Feel free to:
- Add new papers to the bibliography
- Improve the CLI interface
- Enhance visualization features
- Expand test coverage
- Report bugs or suggest improvements



## LLMs Basics


| Title |  Author(s) | Journal | Year | DOI  |  
|-------|------------|---------|------|------|
| Attention is all you need      | Vaswani et al.    | arXiv  | 2017 | [1706.03762] |
| Shampoo: Preconditioned Stochastic Tensor Optimization | Gupta et al. | arXiv | 2018 | [1802.09568] |
| BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | Devlin et al. | arXiv | 2018 | [1810.04805] |
| Language models are unsupervised multitask learners | Radford et al. | OpenAI | 2019 | [unsupervised-multitask] |
| Language Models are Few-Shot Learners | Brown et al. | arXiv | 2020 | [2005.14165] |
| Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention | Katharopoulos et al. | arXiv | 2020 | [2006.16236] |
| Efficient Transformers: A Survey  | Tay et al. |arXiv | 2020 | [2009.06732] |
| Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity | Fedus et al. | ICML | 2022 | [2101.03961] |
| RoFormer: Enhanced Transformer with Rotary Position Embedding | Su et al. | arXiv | 2021 | [2104.09864] |
| LoRA: Low-Rank Adaptation of Large Language Models | Hu et al. | ICLR | 2021 | [2106.09685] |
| Training Compute-Optimal Large Language Models | Hoffmann et al. | arXiv | 2022 | [2203.15556] |
| PaLM: Scaling Language Modeling with Pathways | Chowdhery et al. | arXiv | 2022 | [2204.02311] |
| FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness | Dao et al. | NeurIPS | 2022 | [2205.14135] |
| QLoRA: Efficient Finetuning of Quantized LLMs | Dettmers et al. | arXiv | 2023 | [2305.14314] |
| FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning | Dao | arXiv | 2023 | [2307.08691] |
| YaRN: Efficient Context Window Extension of Large Language Models | Peng et al. | arXiv | 2023 | [2309.00071] |
| Effective Long-Context Scaling of Foundation Models | Xiong et al. | arXiv | 2023 | [2309.16039] |
| Mistral 7B | Jiang et al. | arXiv | 2023 | [2310.06825] |
| Mamba: Linear-Time Sequence Modeling with Selective State Spaces | Gu and Dao | NeurIPS | 2023 | [2312.00752] |
| How to Train Long-Context Language Models (Effectively) | Gao et al. | arXiv | 2024 | [2410.02660] |
| The Zamba2 Suite: Technical Report | Glorion et al. | arXiv | 2024 | [2411.15242] |
| Muon is Scalable for LLM Training | Liu et al. | 2025 | arXiv | [2502.16982] |
| KIMI K2: OPEN AGENTIC INTELLIGENCE | Kimi Team | arXiv | 2025 | [2507.20534] |

## LLM Datasets

| Title |  Author(s) | Journal | Year | DOI  |  
|-------|------------|---------|------|------|
| SQUAD: 100,000+ Questions for Machine Comprehension of Text | Rajpurkar et al. | arXiv | 2016 | [1606.05250] |
| StarCoder 2 and The Stack v2: The Next Generation | Lozhkov et al. | arXiv | 2024 | [2402.19173] |

## Time-Series Foundationnal Models

| Title |  Author(s) | Journal | Year | DOI  |  
|-------|------------|---------|------|------|
| Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting | Lim et al. | arXiv | 2020 | [1912.09363] |
| N-HiTS: Neural Hierarchical Interpolation for Time Series Forecasting | Challu et al. | arXiv | 2022 | [2201.12886] |

## Diffusion


| Title |  Author(s) | Journal | Year | DOI  |  
|-------|------------|---------|------|------|
| Denoising Diffusion Probabilistic Models | Ho et al. | NeurIPS | 2020 | [2006.11239] |
| Generative Diffusion Models on Graphs: Methods and Applications | Liu et al. | arXiv | 2023 | [2302.02591] |
| dLLM: Simple Diffusion Language Modeling | Zhou et al. | arXiv | 2026 | [2602.22661] |


## EB-Models

| Title |  Author(s) | Journal | Year | DOI  |  
|-------|------------|---------|------|------|
| A tutorial on Energy-Based Learning | LeCun et al. | MIT Press | 2006 | [eb-learning] |
| Your Classifier is Secretly an Energy Based Model and You Should Treat it Like One | Grathwohl et al. | arXiv | 2019 | [1912.03263] |
| How to Train Your Energy-Based Models | Song et al. | arXiv | 2021 | [2101.03288] |
| HELMET: How to Evaluate Long-Context Language Models Effectively and Thoroughly | Yen et al. | arXiv | 2024 | [2410.02694] |
| Energy-Based Transformers are Scalable Learners and Thinkers | Gladstone et al. | arXiv | 2025 | [2507.02092] |

## Alignment 


## Tsetlin Machines Articles

| Title |  Author(s) | Journal | Year | DOI  |  
|-------|------------|---------|------|------|
| The Tsetlin Machine -- A Game Theoretic Bandit Driven Approach to Optimal Pattern Recognition with Propositional Logic | Ole-Christoffer Granmo | arXiv | 2018 | [1804.01508] | 
| Label-Critic Tsetlin Machine: A Novel Self-supervised Learning Scheme for Interpretable Clustering | Abouzeid et al. | IEEE | 2022 | [10.1109/ISTM54910.2022.00016]


[10.1109/ISTM54910.2022.00016]: https://ieeexplore.ieee.org/document/9923796
[1606.05250]: https://arxiv.org/abs/1606.05250
[1706.03762]: https://arxiv.org/abs/1706.03762
[1802.09568]: https://arxiv.org/abs/1802.09568
[1804.01508]: https://arxiv.org/abs/1804.01508
[1810.04805]: https://arxiv.org/abs/1810.04805
[1912.03263]: https://arxiv.org/abs/1912.03263
[1912.09363]: https://arxiv.org/abs/1912.09363
[2005.14165]: https://arxiv.org/abs/2005.14165
[2006.11239]: https://arxiv.org/abs/2006.11239
[2006.16236]: https://arxiv.org/abs/2006.16236
[2009.06732]: https://arxiv.org/abs/2009.06732
[2009.06732]: https://arxiv.org/abs/2009.06732
[2101.03288]: https://arxiv.org/abs/2101.03288
[2101.03961]: https://arxiv.org/abs/2101.03961
[2104.09864]: https://arxiv.org/abs/2104.09864
[2106.09685]: https://arxiv.org/abs/2106.09685
[2201.12886]: https://arxiv.org/abs/2201.12886
[2203.15556]: https://arxiv.org/abs/2203.15556
[2203.15556]: https://arxiv.org/abs/2203.15556
[2204.02311]: https://arxiv.org/abs/2204.02311
[2205.14135]: https://arxiv.org/pdf/2205.14135
[2302.02591]: https://arxiv.org/abs/2302.02591
[2302.02591]: https://arxiv.org/abs/2302.02591
[2305.14314]: https://arxiv.org/abs/2305.14314
[2307.08691]: https://arxiv.org/abs/2307.08691
[2309.00071]: https://arxiv.org/abs/2309.00071
[2309.16039]: https://arxiv.org/abs/2309.16039
[2310.06825]: https://arxiv.org/abs/2310.06825
[2312.00752]: https://arxiv.org/abs/2312.00752
[2402.19173]: https://arxiv.org/abs/2402.19173
[2410.02660]: https://arxiv.org/pdf/2410.02660
[2410.02694]: https://arxiv.org/abs/2410.02694
[2411.15242]: https://arxiv.org/abs/2411.15242
[2502.16982]: https://arxiv.org/abs/2502.16982
[2507.02092]: https://arxiv.org/abs/2507.02092
[2507.20534]: https://arxiv.org/abs/2507.20534
[2602.22661]: https://arxiv.org/abs/2602.22661
[unsupervised-multitask]: https://storage.prod.researchhub.com/uploads/papers/2020/06/01/language-models.pdf
[eb-learning]: [unknown](https://www.researchgate.net/publication/200744586_A_tutorial_on_energy-based_learning)

