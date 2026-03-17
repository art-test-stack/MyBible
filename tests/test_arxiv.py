"""Tests for arXiv metadata fetching module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pkg.mybib import arxiv


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_directory:
        yield Path(temp_directory)


@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file for testing."""
    temp_path = temp_dir / "test_file.xml"
    yield temp_path


@pytest.fixture
def sample_arxiv_response():
    """Sample XML response from arXiv API."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <title>Attention Is All You Need</title>
    <author>
      <name>Ashish Vaswani</name>
    </author>
    <author>
      <name>Noam Shazeer</name>
    </author>
    <author>
      <name>Parmar Aidan</name>
    </author>
    <published>2017-06-12T17:58:41Z</published>
    <arxiv:doi>10.48550/arXiv.1706.03762</arxiv:doi>
    <arxiv:journal_ref>NIPS 2017</arxiv:journal_ref>
    <link href="https://arxiv.org/abs/1706.03762"/>
  </entry>
</feed>"""


@pytest.fixture
def sample_arxiv_response_no_doi():
    """Sample XML response from arXiv API without DOI."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <title>Research Paper Without DOI</title>
    <author>
      <name>John Doe</name>
    </author>
    <published>2020-03-15T10:30:00Z</published>
    <link href="https://arxiv.org/abs/2003.06123"/>
  </entry>
</feed>"""


@pytest.fixture
def sample_arxiv_response_no_journal():
    """Sample XML response from arXiv API without journal reference."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <title>Preprint Paper</title>
    <author>
      <name>Jane Smith</name>
    </author>
    <published>2022-01-10T14:20:00Z</published>
    <arxiv:doi>10.48550/arXiv.2201.04000</arxiv:doi>
    <link href="https://arxiv.org/abs/2201.04000"/>
  </entry>
</feed>"""


class TestFetchArxivMetadata:
    """Test fetching metadata from arXiv API."""

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_success(self, mock_get, sample_arxiv_response):
        """Test successfully fetching arXiv metadata."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_arxiv_response.encode("utf-8")
        mock_get.return_value = mock_response

        result = arxiv.fetch_arxiv_metadata("1706.03762")

        assert result["title"] == "Attention Is All You Need"
        assert "Ashish Vaswani" in result["authors"]
        assert "Noam Shazeer" in result["authors"]
        assert "Parmar Aidan" in result["authors"]
        assert result["year"] == 2017
        assert result["doi"] == "10.48550/arXiv.1706.03762"
        assert result["journal"] == "NIPS 2017"
        assert result["link"] == "https://arxiv.org/abs/1706.03762"
        assert result["arxiv_id"] == "1706.03762"

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_multiple_authors(
        self, mock_get, sample_arxiv_response
    ):
        """Test that multiple authors are properly parsed."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_arxiv_response.encode("utf-8")
        mock_get.return_value = mock_response

        result = arxiv.fetch_arxiv_metadata("1706.03762")

        authors = result["authors"]
        assert authors.count(",") == 2  # Three authors separated by commas
        assert "Ashish Vaswani" in authors
        assert "Noam Shazeer" in authors
        assert "Parmar Aidan" in authors

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_no_doi(self, mock_get, sample_arxiv_response_no_doi):
        """Test handling of metadata without DOI (uses arxiv_id as fallback)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_arxiv_response_no_doi.encode("utf-8")
        mock_get.return_value = mock_response

        result = arxiv.fetch_arxiv_metadata("2003.06123")

        assert result["title"] == "Research Paper Without DOI"
        assert result["year"] == 2020
        assert result["doi"] == "2003.06123"  # Falls back to arxiv_id
        assert result["journal"] == "arXiv"

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_no_journal(
        self, mock_get, sample_arxiv_response_no_journal
    ):
        """Test handling of metadata without journal reference."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_arxiv_response_no_journal.encode("utf-8")
        mock_get.return_value = mock_response

        result = arxiv.fetch_arxiv_metadata("2201.04000")

        assert result["title"] == "Preprint Paper"
        assert result["journal"] == "arXiv"  # Default journal
        assert result["year"] == 2022

    @patch("pkg.mybib.arxiv.sys.exit", side_effect=SystemExit)
    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_http_error(self, mock_get, mock_exit):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(SystemExit):
            arxiv.fetch_arxiv_metadata("1706.03762")

    @patch("pkg.mybib.arxiv.sys.exit", side_effect=SystemExit)
    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_not_found(self, mock_get, mock_exit):
        """Test handling when no entry is found."""
        empty_response = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
</feed>"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = empty_response.encode("utf-8")
        mock_get.return_value = mock_response

        with pytest.raises(SystemExit):
            arxiv.fetch_arxiv_metadata("9999.99999")

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_url_formation(self, mock_get, sample_arxiv_response):
        """Test that the correct URL is being formed."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = sample_arxiv_response.encode("utf-8")
        mock_get.return_value = mock_response

        arxiv.fetch_arxiv_metadata("1706.03762")

        # Check that the URL was called correctly
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "export.arxiv.org/api/query" in called_url
        assert "1706.03762" in called_url

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_whitespace_in_title(self, mock_get):
        """Test that whitespace in title is normalized."""
        response_with_newline = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <title>Attention Is All
      You Need
      Really</title>
    <author>
      <name>Vaswani</name>
    </author>
    <published>2017-06-12T17:58:41Z</published>
    <arxiv:doi>10.48550/arXiv.1706.03762</arxiv:doi>
    <arxiv:journal_ref>NIPS 2017</arxiv:journal_ref>
  </entry>
</feed>"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = response_with_newline.encode("utf-8")
        mock_get.return_value = mock_response

        result = arxiv.fetch_arxiv_metadata("1706.03762")

        # Title should have newlines converted to spaces, but preserve existing spaces
        assert "\n" not in result["title"]
        assert "Attention Is All" in result["title"]
        assert "You Need" in result["title"]

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_single_author(self, mock_get):
        """Test handling of single author."""
        single_author_response = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <title>Single Author Paper</title>
    <author>
      <name>Alice Author</name>
    </author>
    <published>2021-05-01T12:00:00Z</published>
    <arxiv:doi>10.48550/arXiv.2105.00001</arxiv:doi>
    <arxiv:journal_ref>Nature</arxiv:journal_ref>
  </entry>
</feed>"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = single_author_response.encode("utf-8")
        mock_get.return_value = mock_response

        result = arxiv.fetch_arxiv_metadata("2105.00001")

        assert result["authors"] == "Alice Author"

    @patch("pkg.mybib.arxiv.requests.get")
    def test_fetch_arxiv_metadata_connection_error(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = Exception("Connection error")

        with pytest.raises(Exception):
            arxiv.fetch_arxiv_metadata("1706.03762")
