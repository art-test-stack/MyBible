"""Tests for BibTeX generation module."""

from pathlib import Path

import pandas as pd

from pkg.mybib.bibtex import generate_bibtex


class TestGenerateBibtex:
    """Test BibTeX generation behavior."""

    def test_prefers_stored_bibtex_when_available(self):
        """Stored BibTeX entries should be used verbatim."""
        stored = "@inproceedings{vaswani2017attention,\n  title={Attention Is All You Need}\n}"
        df = pd.DataFrame(
            [
                {
                    "Title": "Attention Is All You Need",
                    "Authors": "A. Vaswani",
                    "Journal": "NeurIPS",
                    "Year": 2017,
                    "DOI": "10.1234/attention",
                    "Link": "https://arxiv.org/abs/1706.03762",
                    "BibTeX": stored,
                }
            ]
        )

        result = generate_bibtex(df)
        assert result == stored

    def test_falls_back_to_generated_entry_without_stored_bibtex(self):
        """Missing BibTeX should still produce generated BibTeX entries."""
        df = pd.DataFrame(
            [
                {
                    "Title": "Fallback Paper",
                    "Authors": "A. Author",
                    "Journal": "Journal",
                    "Year": 2026,
                    "DOI": "10.1234/fallback",
                    "Link": "https://example.com/fallback",
                }
            ]
        )

        result = generate_bibtex(df)
        assert "@article{10.1234/fallback" in result
        assert "title={Fallback Paper}" in result

    def test_reads_bibtex_from_path(self, tmp_path):
        """BibTeX path should be preferred when file exists."""
        bib_dir = tmp_path / "bibtex_entries"
        bib_dir.mkdir()
        bib_file = bib_dir / "entry.bib"
        bib_file.write_text("@misc{path_entry, title={From Path}}\n", encoding="utf-8")

        csv_file = tmp_path / "references.csv"
        df = pd.DataFrame(
            [
                {
                    "Title": "Path Paper",
                    "Authors": "A. Author",
                    "Journal": "Journal",
                    "Year": 2026,
                    "DOI": "10.1234/path",
                    "Link": "https://example.com/path",
                    "BibTeXPath": "bibtex_entries/entry.bib",
                }
            ]
        )

        result = generate_bibtex(df, csv_file=str(csv_file))
        assert result == "@misc{path_entry, title={From Path}}"
