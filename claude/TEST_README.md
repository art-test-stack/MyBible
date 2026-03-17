# MyBible Test Suite

This directory contains comprehensive pytest tests for the MyBible bibliography management package.

## Test Modules

### test_storage.py
Tests for the CSV storage module (`pkg/mybib/storage.py`):
- **TestAddReference**: Tests adding references to the CSV file
  - Adding to empty files
  - Adding multiple references
  - Header preservation
- **TestDuplicateDetection**: Tests duplicate reference detection
  - DOI-based duplicate detection
  - Case-insensitive matching
  - Whitespace normalization
  - Different DOIs are not flagged as duplicates
- **TestLoadReferences**: Tests loading references from storage
  - Loading from existing files
  - Creating empty structure for new files
  - Data preservation

**Coverage**: Adding references, duplicate detection with case-insensitive and whitespace normalization

### test_arxiv.py
Tests for arXiv metadata fetching module (`pkg/mybib/arxiv.py`):
- **TestFetchArxivMetadata**: Tests arXiv API metadata fetching
  - Successful metadata fetching with multiple authors
  - Multiple author parsing
  - Fallback DOI handling (using arxiv_id when DOI not available)
  - Default journal reference handling
  - HTTP error handling
  - No entry found handling
  - URL formation verification
  - Title whitespace normalization
  - Single author handling
  - Connection error handling

**Coverage**: arXiv metadata parsing with mocked HTTP requests

**Mock Implementation**: Uses `unittest.mock.patch` to mock `requests.get` and `sys.exit` calls, preventing actual network requests.

### test_markdown.py
Tests for markdown generation module (`pkg/mybib/markdown.py`):
- **TestMakeMarkdownTable**: Tests basic markdown table generation
  - Empty reference handling
  - Single and multiple references
  - Sorting by category and year
  - DOI formatting
  - Author name reformatting
  - Valid markdown syntax
- **TestMakeMarkdownTablesByCategory**: Tests category-separated markdown output
  - Empty file handling
  - Single and multiple categories
  - Column exclusion (Link, Category)
  - Footer link generation
  - Link deduplication
  - Category and year sorting
- **TestReformNames**: Tests author name reformatting utility
  - Single author (last name only)
  - Two authors ("LastName1 and LastName2")
  - Three+ authors ("LastName et al.")
  - Names with middle names
  - Names with suffixes
- **TestPrepareReferencesForMarkdown**: Tests internal preparation function

**Coverage**: Markdown generation, author name reformatting, sorting and formatting

## Running the Tests

### Prerequisites

Ensure you have pytest and dev dependencies installed:

```bash
cd /Users/arthurtestard/MyBible
source .venv/bin/activate
pip install -e ".[dev]"
```

Or install directly:

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# From the project root
python -m pytest tests/ -v
```

### Run Specific Test Module

```bash
# Storage tests
python -m pytest tests/test_storage.py -v

# ArXiv tests
python -m pytest tests/test_arxiv.py -v

# Markdown tests
python -m pytest tests/test_markdown.py -v
```

### Run Specific Test Class

```bash
python -m pytest tests/test_storage.py::TestDuplicateDetection -v
```

### Run Specific Test

```bash
python -m pytest tests/test_storage.py::TestDuplicateDetection::test_duplicate_doi_detection -v
```

### Generate Coverage Report

```bash
# Terminal report
python -m pytest tests/ --cov=pkg/mybib --cov-report=term-missing

# HTML report
python -m pytest tests/ --cov=pkg/mybib --cov-report=html
# Open htmlcov/index.html in browser
```

### Run with Verbose Output

```bash
python -m pytest tests/ -v -s
```

The `-s` flag shows print statements from tests.

## Test Configuration

The `pytest.ini` file contains test configuration:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## Test Statistics

- **Total Tests**: 61
- **Test Modules**: 3
- **Main Coverage Areas**:
  - Storage operations (adding, loading, duplicate detection)
  - ArXiv metadata fetching (with mocked API calls)
  - Markdown generation (tables, category separation, formatting)

## Mock Implementation

The tests use `unittest.mock` to mock external dependencies:

### ArXiv Tests (test_arxiv.py)
- **Mocked**: `requests.get` - Prevents actual API calls to arXiv
- **Mocked**: `sys.exit` - Prevents test process termination
- **Purpose**: Test API response parsing with various scenarios without network dependency

Example:
```python
@patch('pkg.mybib.arxiv.requests.get')
def test_fetch_arxiv_metadata_success(self, mock_get, sample_arxiv_response):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = sample_arxiv_response.encode('utf-8')
    mock_get.return_value = mock_response
    # Test proceeds with mocked response
```

### Storage Tests (test_storage.py)
- **Mocked**: `sys.exit` - For testing duplicate detection behavior
- **Uses temporary files**: Each test gets a fresh temporary CSV file
- **Cleanup**: Temporary files are automatically deleted after tests

## Notes

- All tests use temporary CSV files to avoid side effects
- Network requests are fully mocked, making tests run fast and reliably
- Tests cover both happy paths and error scenarios
- Author name reformatting behavior is well-tested for various input formats
- Duplicate detection is case-insensitive and handles whitespace variations
