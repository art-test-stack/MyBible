# Google Scholar Integration for MyBible

## Overview

The MyBible bibliography management system now includes integration with Google Scholar via the SerpAPI. This allows users to:

1. **Search Google Scholar** for articles by title or URL
2. **Automatically fetch metadata** including authors, journal, year, and publication info
3. **Seamlessly add articles** with user confirmation before storing

## Features

### New Commands

#### `mybib add-scholar`
Search and add articles from Google Scholar by title or URL.

```bash
# Search by title
mybib add-scholar --title "Machine Learning" --category ML

# Search by URL
mybib add-scholar --url "https://example.com/paper.pdf" --category Science
```

#### `mybib add` (Enhanced)
Now supports automatic Google Scholar lookup when only title is provided.

```bash
# Manual entry with all details
mybib add --title "Paper" --authors "Author" --journal "Nature" --year 2024 --doi "10.xxxx" --category Science

# Automatic Google Scholar search with only title
mybib add --title "Machine Learning Overview"

# Partial entry - fills in missing fields from Google Scholar
mybib add --title "Paper" --authors "Author Name"
```

### How It Works

#### When Using `add` Command with Only Title:
1. User provides only `--title` (and optionally `--category`)
2. System searches Google Scholar for matching articles
3. Shows the top result to the user
4. User confirms if it's the correct article
5. If confirmed, article metadata is added to references
6. If not confirmed, system shows additional results to choose from

#### When Using Existing Commands:
- The existing `add-arxiv` command continues to work as before
- Authors can still manually specify all fields
- Partial information is automatically completed from Google Scholar

## Configuration

### Setup SerpAPI Key

The integration requires a SerpAPI API key. You can get a free key at https://serpapi.com.

Set the environment variable:

```bash
export SERPAPI_KEY="your-api-key-here"
```

For development, you can add this to your `.env` file or shell configuration.

### Free API Tier

- **Free Plan**: 250 searches/month
- **Usage**: Each Google Scholar search and BibTeX fetch counts as one search

## Technical Details

### New Module: `scholar.py`

Located at `pkg/mybib/scholar.py`, this module provides:

- `search_google_scholar(query, max_results)` - Search for articles
- `extract_metadata_from_result(result)` - Parse Google Scholar result into standardized format
- `search_and_confirm_article(title, max_attempts)` - Interactive search with user confirmation
- `fetch_bibtex_from_scholar(result_id)` - Fetch BibTeX citation (for future use)

### Integration with Existing Code

The new functionality integrates with:
- `storage.py` - Stores references in CSV format
- `ui.py` - User interaction and confirmation
- `cli.py` - Command-line interface

## Examples

### Example 1: Add Paper by Title Only

```bash
$ mybib add --title "Attention Is All You Need"

[CY AN]Searching Google Scholar for your article...[/CYAN]

[YELLOW]Found:[/YELLOW]
Title: Attention Is All You Need
Authors: A Vaswani, N Shazeer, P Parmar, ...
Journal: arXiv, 2017
Year: 2017

Is this the correct article? [y/N]: y

Enter category for 'Attention Is All You Need': ML

Add 'Attention Is All You Need' to category 'ml'? [y/N]: y

✓ Added: Attention Is All You Need
```

### Example 2: Using add-scholar Command

```bash
$ mybib add-scholar --title "Deep Learning" --category AI

[CYAN]Searching Google Scholar for: Deep Learning[/CYAN]

[YELLOW]Option 1:[/YELLOW]
Title: Deep Learning
Authors: I Goodfellow, Y Bengio, A Courville
Journal: MIT press, 2016
Year: 2016

Is this the correct article? [y/N]: y

Add 'Deep Learning' to category 'ai'? [y/N]: y

✓ Added: Deep Learning
```

### Example 3: Fallback to Manual Entry

If Google Scholar search doesn't find the correct article, users can:

1. Provide additional metadata fields when calling `add`
2. All provided fields take precedence over Google Scholar search
3. Missing fields are filled in from Google Scholar or left empty

```bash
$ mybib add --title "My Paper" --authors "John Doe" --year 2024
```

## Error Handling

### Missing API Key
```
Error: SERPAPI_KEY environment variable not set.
Get a free API key at https://serpapi.com
```

### No Results Found
```
[RED]No results found on Google Scholar[/RED]
```

### API Rate Limit
The system will show an error if you exceed the free tier limit. Consider upgrading your SerpAPI plan.

## Future Enhancements

1. **BibTeX Auto-Import**: Fetch and parse BibTeX directly from Google Scholar
2. **Caching**: Cache search results to reduce API calls
3. **Batch Processing**: Add multiple papers at once with a search query
4. **Advanced Filters**: Search with author names, year ranges, etc.
5. **Crossref Integration**: Fall back to Crossref API for DOI lookups

## Testing

To test the Google Scholar integration:

1. Set your `SERPAPI_KEY` environment variable
2. Run a simple search:
   ```bash
   mybib add --title "Test Paper Title"
   ```

3. Verify the CLI shows results from Google Scholar
4. Confirm the article is added to your references CSV

## Troubleshooting

### "Command not found: mybib"
Make sure your virtual environment is activated:
```bash
source .venv/bin/activate
```

### "SERPAPI_KEY not set"
Set your API key:
```bash
export SERPAPI_KEY="your-key"
```

### "No results on Google Scholar"
Try:
1. Using a simpler, shorter title
2. Searching by author name or year
3. Manually entering the details using `mybib add --title ... --authors ...`

## Contributing

To contribute improvements:
1. See the `scholar.py` module for the integration logic
2. Test changes in a virtual environment
3. Update this documentation with new features

---

**Version**: 1.0  
**Last Updated**: March 2026
