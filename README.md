# 📚 MyBible - Research Paper Bibliography Manager

A modern, feature-rich CLI tool for managing a curated collection of research papers with beautiful terminal output, interactive visualizations, and comprehensive testing.

## Overview

MyBible is a comprehensive bibliography management system designed to help researchers organize, track, and analyze their research paper collections. This repository contains a curated list of important research papers (primarily from AI research) with tools to:

- ✨ **Add papers** from arXiv or manually with beautiful CLI prompts
- 🔗 **Add repositories** from GitHub and Hugging Face
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
git clone git@github.com:art-test-stack/MyBible.git
cd MyBible
uv sync
```

### Adding Papers

#### From arXiv
```bash
mybib add-arxiv <arxiv_url> --category <category_name>
```

Example:
```bash
mybib add-arxiv https://arxiv.org/abs/2401.00001 --category "Machine Learning"
```

#### Automated Google Scholar Search
```bash
mybib add --title "Attention is all you need" --category "Machine Learning"
```

#### From GitHub or Hugging Face
```bash
mybib add-repo <repo_url> --category <category_name>
```

Examples:
```bash
mybib add-repo https://github.com/openai/whisper --category "Speech"
mybib add-repo https://huggingface.co/google/gemma-2-2b --category "LLM"
```

#### Manual Entry
```bash
mybib add --title "<title>" --authors "<author1>, <author2>, ..." \
  --journal "<journal>" --year <year> --doi "<doi>" --category <category>
```

### Generating Output

#### Markdown Tables
```bash
mybib markdown --file references.csv --output references.md
```

#### BibTeX Export
```bash
mybib bibtex --file references.csv --output references.bib
```

#### Backfill Missing BibTeX
```bash
mybib sync-bibtex --file references.csv
```

This stores BibTeX entries in files under `bibtex_entries/` (configurable), and keeps only paths in `references.csv`.

#### Citation Network Graph
```bash
mybib graph --file references.csv --output citation_graph.html
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

Add 'Attention is all you need' to category 'Machine Learning'? [y/N]: y
✓ Reference added successfully to category 'Machine Learning'
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

When available, MyBible now fetches and stores source BibTeX entries in files:
- `add-arxiv` fetches citation BibTeX from arXiv
- `add-repo` fetches citation BibTeX from repository README files (GitHub/Hugging Face)
- `sync-bibtex` backfills missing BibTeX for references already stored in CSV

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

## 🎯 Recent Improvements (v2.0)

### ✨ Enhanced Data Quality

**Authors Formatting**
- Proper "FirstAuthor et al." format instead of just "al."
- Team name detection and display (K2 Team, DeepSeek-Ai, Mistral, etc.)
- Intelligently handles both individual and organizational authors

**ArxivID Precision**
- Fixed float rounding errors (2405.10938 now displays correctly, not 2405.11)
- ArxivID stored as string to preserve full precision

**Scholar Metadata Extraction**
- Improved year extraction for Google Scholar articles (full 4-digit years)
- Better DOI extraction with intelligent fallback to Scholar IDs
- Enhanced regex patterns for robust metadata parsing

### 🏷️ Category Management System

- **ID-based categories**: Each category assigned a unique ID with persistent mappings
- **Case-insensitive normalization**: "LLM Basics" and "llm basics" treated as same category
- **Interactive selection**: Choose categories by ID or create new ones on-the-fly
- **Category persistence**: All mappings stored in `categories.json`

```bash
# Interactive category selection during add
mybib add-arxiv https://arxiv.org/abs/2301.00001
# Shows: Available categories: 1: Alignment, 2: Deep Learning, 3: Machine Learning
```

### 🗄️ Database Foundation (SQLAlchemy ORM)

Scalable SQL database support for advanced features:

**New Commands:**
```bash
# Initialize database
mybib db-init --db-url sqlite:///bibliography.db

# Migrate existing CSV to database
mybib db-migrate --file references.csv --db-url sqlite:///bibliography.db

# Export database back to CSV
mybib db-export --output backup.csv --db-url sqlite:///bibliography.db
```

**Features:**
- SQLite default, supports any SQLAlchemy-compatible database (PostgreSQL, MySQL, etc.)
- Full referential integrity with foreign keys
- Indexed queries for common search patterns
- Non-destructive migration (export back to CSV anytime)
- Duplicate detection based on DOI

**Benefits:**
- Foundation for advanced search and filtering
- Ready for future enhancements (tags, annotations, full-text search)
- Better performance with large reference collections
- API layer ready for remote access

## Architecture

### Project Structure

```
MyBible/
├── pkg/mybib/              # Main package
│   ├── __init__.py
│   ├── cli.py              # CLI command handlers
│   ├── storage.py          # CSV storage operations
│   ├── arxiv.py            # arXiv API integration
│   ├── scholar.py          # Google Scholar integration
│   ├── citation.py         # Citation BibTeX fetching and parsing
│   ├── metadata.py         # Metadata management
│   ├── markdown.py         # Markdown generation
│   ├── bibtex.py           # BibTeX export
│   ├── graph.py            # Citation graph features
│   ├── ui.py               # Terminal UI utilities
│   ├── utils.py            # Utility functions
│   ├── categories.py       # Category management system
│   ├── models.py           # SQLAlchemy ORM models
│   └── db_storage.py       # Database storage adapter
├── tests/                  # Test suite
│   ├── test_storage.py
│   ├── test_arxiv.py
│   ├── test_markdown.py
│   ├── test_metadata.py
│   ├── test_scholar.py
│   └── __init__.py
├── references.csv          # Bibliography database (CSV)
├── categories.json         # Category ID mappings
├── pyproject.toml          # Project configuration
├── pytest.ini              # Pytest configuration
├── IMPROVEMENTS_SUMMARY.md # Detailed changelog for v2.0
└── README.md              # This file
```

### Core Modules

- **`cli.py`**: Command-line interface with rich formatting and category prompts
- **`storage.py`**: CSV file handling with ArxivID support and duplicate detection
- **`arxiv.py`**: arXiv metadata fetching with error handling
- **`scholar.py`**: Google Scholar integration with improved metadata extraction
- **`citation.py`**: BibTeX extraction from arXiv and repository README files
- **`metadata.py`**: Reference metadata management
- **`markdown.py`**: Markdown table generation with category support and author formatting
- **`bibtex.py`**: BibTeX export functionality
- **`graph.py`**: Citation network building and visualization
- **`ui.py`**: Terminal UI components (colors, progress, confirmations)
- **`categories.py`**: Category management with ID-based persistence
- **`models.py`**: SQLAlchemy ORM models for database support
- **`db_storage.py`**: Database storage adapter with migration capabilities
- **`utils.py`**: Utility functions including enhanced author name formatting

## Dependencies

Core dependencies (installed via `uv sync`):
- `pandas`: CSV data handling
- `requests`: HTTP requests for APIs
- `rich`: Beautiful terminal output
- `networkx`: Graph algorithms and data structures
- `pyvis`: Interactive network visualization
- `sqlalchemy`: ORM framework for database abstraction

Development dependencies:
- `pytest`: Testing framework
- `pytest-cov`: Code coverage reporting

[!Note]
See `tests/README.md` for details on the comprehensive test suite covering modules.

## CLI Commands

### Reference Management
```bash
# View help
mybib --help

# Add reference from arXiv
mybib add-arxiv https://arxiv.org/abs/2301.00001 [--category <name>]

# Add reference from GitHub or Hugging Face repository
mybib add-repo <repo_url> [--category <name>]

# Add reference from Google Scholar (with interactive search)
mybib add-scholar --title "<article name>" [--category <name>]

# Add reference manually
mybib add --title "<title>" [--authors] [--journal] [--year] [--doi] [--category]

# Fetch and store missing BibTeX for existing references
mybib sync-bibtex [--file references.csv] [--force] [--bibtex-dir bibtex_entries]

# View help for specific commands
mybib add-arxiv --help
mybib add-repo --help
mybib add-scholar --help
mybib add --help
mybib sync-bibtex --help
```

### Output Generation
```bash
# Generate markdown tables
mybib markdown --file references.csv --output references.md [--by-category]

# Generate BibTeX file
mybib bibtex --file references.csv --output references.bib

# Build citation network graph
mybib graph --file references.csv --output citation_graph.html [--verbose]
```

### Database Operations (v2.0)
```bash
# Initialize database
mybib db-init [--db-url sqlite:///bibliography.db]

# Migrate CSV to database
mybib db-migrate --file references.csv [--db-url sqlite:///bibliography.db]

# Export database back to CSV
mybib db-export --output backup.csv [--db-url sqlite:///bibliography.db]
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
- **ArxivID**: arXiv identifier (optional)
- **BibTeX**: Legacy inline BibTeX field (kept for backward compatibility)
- **BibTeXPath**: Path to BibTeX file stored on disk

Categories are managed in `categories.json` with ID-to-name mappings for case-insensitive organization.

## Changelog

### v2.0 (Latest)

Major improvements to data quality and scalability:

**✨ Improvements:**
- Auto format authors as "FirstAuthor et al." with team name detection
- Fixed ArxivID display precision (no more float rounding errors)
- Enhanced Scholar metadata extraction (full year extraction, better DOI finding)
- New category management system with persistent ID mappings
- Foundation for database support with SQLAlchemy ORM

**New Features:**
- Database initialization and migration commands
- CSV ↔ Database conversion tools
- Interactive category selection by ID during reference addition

**See [`IMPROVEMENTS_SUMMARY.md`](IMPROVEMENTS_SUMMARY.md) for detailed technical documentation.**

### v1.0

Initial release with CSV-based storage, arXiv/Scholar/manual entry, markdown/BibTeX export, and citation graph visualization.

## Future Enhancements

Potential features enabled by v2.0 database foundation:
- Advanced search and filtering
- Paper summaries and reading notes
- Reading progress tracking
- Topic clustering visualization
- Export to other formats (RIS, Zotero)
- Full-text search capabilities
- Tag and annotation system
- API layer for remote access

## Contributing

Contributions are welcome! Feel free to:
- Improve the CLI interface
- Enhance visualization features
- Expand test coverage
- Report bugs or suggest improvements

## Aknowledgements
- Inspired by my need for better bibliography management tools. After struggling with manual CSV files and clunky reference managers, I wanted a modern, customizable solution that fits my workflow. MyBible is the result of that vision. Alternatively, there are [paperlib](https://github.com/Future-Scholars/paperlib) which seems to be a better tool for general use cases.
- I have started this project with "traditional" coding practices, but at some point (exactly from commit [d8f992f](https://github.com/art-test-stack/MyBible/commit/d8f992f263cfc8657ec13dd3b657f4d548e71a6e)) I have switched to "vibe coding" practices with Claude Haiku 4.5. Hence, I have not written most of the features. 
- The project is still in early stages, so there are many rough edges and missing features. Hence, it is mainly for my personal use, so it works well for computer science research. I am open to contributions and suggestions to make it better!

# Example of output markdown table generated by `mybib markdown`

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

