
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
