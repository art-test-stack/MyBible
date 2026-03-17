# Quick Start Guide - Google Scholar Integration

## Installation & Setup

### 1. Get Your API Key (Free)
1. Visit https://serpapi.com
2. Sign up for a free account
3. Copy your API key from the dashboard

### 2. Set Environment Variable
```bash
# Temporary (current session only)
export SERPAPI_KEY="your-api-key-here"

# Permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export SERPAPI_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Activate Virtual Environment
```bash
cd /Users/arthurtestard/MyBible
source .venv/bin/activate
```

## Usage Examples

### Example 1: Search by Title Only ⭐ (Easiest)
```bash
mybib add --title "Attention Is All You Need"
```
- System automatically searches Google Scholar
- Shows the top result
- You confirm if it's correct
- Article added!

### Example 2: Dedicated Scholar Command
```bash
mybib add-scholar --title "Deep Learning" --category AI
```
- Explicit Google Scholar search
- Add category upfront if desired
- Same confirmation flow

### Example 3: With URL Instead of Title
```bash
mybib add-scholar --url "https://arxiv.org/abs/2301.00001"
```
- Searches Scholar based on the URL
- Useful when you have a direct link

### Example 4: Partial Information
```bash
mybib add --title "Neural Networks" --authors "Geoffrey Hinton"
```
- Combines your info with Scholar search
- More targeted results
- Still asks for confirmation

### Example 5: Existing Commands Still Work
```bash
# arXiv - works as before
mybib add-arxiv https://arxiv.org/abs/2301.00001 --category ML

# Manual entry - all fields optional now (except title)
mybib add --title "Paper" --journal "Nature" --year 2024

# Manual entry - complete information
mybib add \
  --title "Machine Learning" \
  --authors "Ian Goodfellow, Yoshua Bengio" \
  --journal "MIT Press" \
  --year 2016 \
  --doi "10.xxxx/xxxxx" \
  --link "https://deeplearningbook.org" \
  --category Science
```

## Workflow

```
User Command
    ↓
CLI parses arguments
    ↓
Does it have only title (no other fields)?
    ├─ YES → Search Google Scholar
    │          ↓
    │       Show top result
    │          ↓
    │       User confirms? → NO → Show more results
    │       ↓ YES
    │       Add to CSV
    │
    └─ NO → Use provided data, no search
             ↓
          Ask for category if missing
             ↓
             Add to CSV
```

## What Gets Stored

After confirming an article, MyBible stores:
- **Title** - Article title
- **Authors** - Author names (comma-separated)
- **Journal** - Publication source
- **Year** - Publication year
- **DOI** - Digital Object Identifier
- **Link** - URL to the article
- **Category** - Your custom category

## What Happens When...

### User confirms first result
✓ Article added immediately
✓ Metadata saved to CSV
✓ Ready to generate PDFs, graphs, markdown

### User says NO to first result
- Shows next results (up to 3 attempts)
- User picks the correct one
- Same confirmation and storage

### No results found on Scholar
- Graceful error message
- User can provide manual data instead
- Or try a different search term

### SERPAPI_KEY not set
```
Error: SERPAPI_KEY environment variable not set.
Get a free API key at https://serpapi.com
```
**Solution**: Scroll up to "Set Environment Variable" section

## Common Tasks

### Task: Add 5 Papers Quickly
```bash
mybib add --title "Deep Learning"              # Paper 1
mybib add --title "Neural Architecture Search" # Paper 2
mybib add --title "Transformer Models"         # Paper 3
mybib add --title "Attention Mechanisms"       # Paper 4
mybib add --title "BERT Language Model"        # Paper 5
```

### Task: Generate Bibliography
```bash
# After adding papers, generate markdown
mybib markdown --file references.csv --output README.md

# Or BibTeX for LaTeX
mybib bibtex --file references.csv --output references.bib
```

### Task: See All Commands
```bash
mybib --help
```

### Task: See Help for Specific Command
```bash
mybib add --help
mybib add-scholar --help
mybib add-arxiv --help
```

## Tips & Tricks

### 💡 Tip 1: Be Specific
❌ Bad: `mybib add --title "Learning"`
✓ Good: `mybib add --title "Deep Learning for Computer Vision"`

### 💡 Tip 2: Add Category Later
If unsure about category:
```bash
mybib add --title "Paper Name"
# When prompted: Leave blank and press Enter to add later manually
```

### 💡 Tip 3: Check Before Adding
The system shows you the article before confirming:
```
Title: Attention Is All You Need
Authors: A Vaswani, N Shazeer, P Parmar, J Uszkoreit, L Jones, AN Gomez, L Kaiser, I Polosukhin
Journal: arXiv, 2017
Year: 2017
```

Review this carefully! Say NO if any detail is wrong.

### 💡 Tip 4: Use Full Titles
More successful searches:
- ✓ "Attention Is All You Need" (exact title)
- ✓ Author names help: "Attention Is All You Need Vaswani"
- ✗ "attention" (too generic)

### 💡 Tip 5: Free Tier Limit
You get 250 searches/month (about 8-10 active sessions). That's plenty for most users!

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `SERPAPI_KEY not set` | Run `export SERPAPI_KEY="your-key"` |
| Article not found | Try a simpler title or author name |
| "Command not found: mybib" | Activate venv: `source .venv/bin/activate` |
| Import errors | Make sure you're in the right directory: `cd /Users/arthurtestard/MyBible` |

## Data Flow

```
Google Scholar
      ↓
SerpAPI (free tier)
      ↓
scholar.py module
      ↓
cli.py handlers
      ↓
storage.py
      ↓
references.csv
      ↓
markdown.py, bibtex.py, graph.py
      ↓
Your outputs!
```

## Useful Links

- **SerpAPI**: https://serpapi.com (free API key)
- **Google Scholar**: https://scholar.google.com (where data comes from)
- **MyBible Project**: See README.md in this directory

## Next Steps

1. ✅ Set SERPAPI_KEY environment variable
2. ✅ Try: `mybib add --title "Your Favorite Paper"`
3. ✅ Confirm the article shown is correct
4. ✅ Verify it was added: Open `references.csv`
5. ✅ Generate markdown: `mybib markdown --output README.md`
6. ✅ Look at the output!

---

**Questions?** Check GOOGLE_SCHOLAR_README.md for detailed documentation  
**Want advanced features?** See IMPLEMENTATION_SUMMARY.md for technical details
