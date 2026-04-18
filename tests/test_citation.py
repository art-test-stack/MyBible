"""Tests for citation BibTeX fetching helpers."""

import base64
from unittest.mock import Mock, patch

from pkg.mybib import citation


class TestCitationExtraction:
    """Test BibTeX extraction helpers."""

    def test_extract_bibtex_from_markdown_fenced_block(self):
        """Should extract BibTeX from fenced bibtex markdown block."""
        markdown = (
            "Some text\n"
            "```bibtex\n"
            "@article{key,\n  title={Sample Title}\n}\n"
            "```\n"
        )

        result = citation._extract_bibtex_from_markdown(markdown)
        assert result.startswith("@article{key")
        assert "title={Sample Title}" in result

    @patch("pkg.mybib.citation.requests.get")
    def test_fetch_arxiv_bibtex(self, mock_get):
        """Should fetch and parse BibTeX from arXiv bibtex page."""
        html = "<html><body><pre>@article{arxiv_key, title={Arxiv Title}}</pre></body></html>"
        mock_response = Mock()
        mock_response.text = html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = citation.fetch_arxiv_bibtex("2301.00001")
        assert result == "@article{arxiv_key, title={Arxiv Title}}"

    @patch("pkg.mybib.citation.requests.get")
    def test_fetch_repo_bibtex_github_readme(self, mock_get):
        """Should decode GitHub README and extract a BibTeX block."""
        readme = (
            "# Project\n\n"
            "```bibtex\n"
            "@misc{repo_key,\n  title={Repo Title}\n}\n"
            "```\n"
        )
        encoded = base64.b64encode(readme.encode("utf-8")).decode("utf-8")

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"content": encoded}
        mock_get.return_value = mock_response

        result = citation.fetch_repo_bibtex("https://github.com/openai/whisper")
        assert result.startswith("@misc{repo_key")
        assert "title={Repo Title}" in result

    def test_fetch_bibtex_for_row_from_github_doi_key(self):
        """Should reconstruct repo URL from synthetic DOI key for backfill."""
        with patch("pkg.mybib.citation.fetch_repo_bibtex") as mock_fetch:
            mock_fetch.return_value = "@misc{repo_key, title={Repo}}"
            result = citation.fetch_bibtex_for_row(doi="github:openai/whisper")

        mock_fetch.assert_called_once_with("https://github.com/openai/whisper")
        assert result == "@misc{repo_key, title={Repo}}"
