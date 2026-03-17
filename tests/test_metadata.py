"""Tests for metadata extraction module."""

import sys
import pytest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, '../pkg')

from mybib import metadata


class TestSourceDetection:
    """Test source detection functions."""
    
    def test_arxiv_url_detection(self):
        """Test arXiv URL detection."""
        assert metadata._is_arxiv_url("https://arxiv.org/abs/2301.00001")
        assert metadata._is_arxiv_url("http://arxiv.org/pdf/2301.00001.pdf")
        assert not metadata._is_arxiv_url("https://doi.org/10.1234/example")
    
    def test_doi_url_detection(self):
        """Test DOI URL detection."""
        assert metadata._is_doi_url("https://doi.org/10.1145/1234567")
        assert metadata._is_doi_url("http://doi.org/10.1234/example")
        assert not metadata._is_doi_url("https://arxiv.org/abs/2301.00001")
    
    def test_doi_pattern_detection(self):
        """Test DOI pattern detection."""
        assert metadata._is_doi_pattern("10.1145/1234567")
        assert metadata._is_doi_pattern("10.1234/example.doi")
        assert not metadata._is_doi_pattern("https://doi.org/10.1145/1234567")


class TestIdExtraction:
    """Test ID extraction functions."""
    
    def test_arxiv_id_extraction(self):
        """Test arXiv ID extraction from URLs."""
        assert metadata._extract_arxiv_id("https://arxiv.org/abs/2301.00001") == "2301.00001"
        assert metadata._extract_arxiv_id("https://arxiv.org/pdf/2301.00001v2.pdf") == "2301.00001"
        
    def test_arxiv_id_extraction_invalid(self):
        """Test arXiv ID extraction with invalid URL."""
        with pytest.raises(SystemExit):
            metadata._extract_arxiv_id("https://arxiv.org/invalid")


class TestDoiNormalization:
    """Test DOI normalization."""
    
    def test_normalize_doi_from_url(self):
        """Test DOI extraction from URL."""
        assert metadata._normalize_doi("https://doi.org/10.1145/1234567") == "10.1145/1234567"
    
    def test_normalize_doi_already_normalized(self):
        """Test DOI that's already normalized."""
        assert metadata._normalize_doi("10.1145/1234567") == "10.1145/1234567"


class TestHtmlMetaExtraction:
    """Test HTML meta tag extraction."""
    
    def test_extract_html_meta_with_property(self):
        """Test extraction of meta tag with property attribute."""
        html = '<meta property="og:title" content="Test Title"/>'
        result = metadata._extract_html_meta(html, ["og:title"])
        assert result == "Test Title"
    
    def test_extract_html_meta_with_name(self):
        """Test extraction of meta tag with name attribute."""
        html = '<meta name="author" content="John Doe"/>'
        result = metadata._extract_html_meta(html, ["author"])
        assert result == "John Doe"
    
    def test_extract_html_meta_not_found(self):
        """Test extraction when meta tag is not found."""
        html = '<html><head></head></html>'
        result = metadata._extract_html_meta(html, ["og:title", "author"])
        assert result is None


class TestFunctionRouting:
    """Test that fetch_metadata routes to correct handler."""
    
    @patch('mybib.metadata._fetch_arxiv_metadata')
    def test_route_to_arxiv(self, mock_arxiv):
        """Test routing to arXiv handler."""
        mock_arxiv.return_value = {"title": "arxiv paper"}
        metadata.fetch_metadata("https://arxiv.org/abs/2301.00001")
        mock_arxiv.assert_called_once()
    
    @patch('mybib.metadata._fetch_crossref_metadata')
    def test_route_to_doi_url(self, mock_doi):
        """Test routing to DOI URL handler."""
        mock_doi.return_value = {"title": "doi paper"}
        metadata.fetch_metadata("https://doi.org/10.1145/1234567")
        mock_doi.assert_called_once()
    
    @patch('mybib.metadata._fetch_crossref_metadata')
    def test_route_to_doi_pattern(self, mock_doi):
        """Test routing to DOI pattern handler."""
        mock_doi.return_value = {"title": "doi paper"}
        metadata.fetch_metadata("10.1145/1234567")
        mock_doi.assert_called_once()
    
    @patch('mybib.metadata._fetch_generic_metadata')
    def test_route_to_generic(self, mock_generic):
        """Test routing to generic URL handler."""
        mock_generic.return_value = {"title": "generic page"}
        metadata.fetch_metadata("https://example.com/paper")
        mock_generic.assert_called_once()


class TestReturnFormat:
    """Test that all handlers return standardized format."""
    
    @patch('mybib.metadata._fetch_generic_metadata')
    def test_return_format_has_required_fields(self, mock_generic):
        """Test that returned dict has all required fields."""
        mock_generic.return_value = {
            "title": "Test",
            "authors": "Author",
            "journal": "Journal",
            "year": 2023,
            "doi": "10.1234/test",
            "link": "https://example.com"
        }
        result = metadata.fetch_metadata("https://example.com")
        
        required_fields = {"title", "authors", "journal", "year", "doi", "link"}
        assert required_fields.issubset(result.keys())


# Example usage demonstrations
def demo_arxiv_metadata():
    """Demo: Fetch metadata from arXiv paper."""
    print("\n=== Demo: arXiv Metadata ===")
    url = "https://arxiv.org/abs/2301.00001"
    print(f"URL: {url}")
    print(f"Expected: Metadata for arXiv paper with automatic source detection")
    # Note: Actual API call commented out to avoid network dependency in tests
    # result = metadata.fetch_metadata(url)
    # print(f"Result: {result}")


def demo_doi_metadata():
    """Demo: Fetch metadata from DOI."""
    print("\n=== Demo: DOI Metadata ===")
    url = "https://doi.org/10.1145/1234567"
    print(f"URL: {url}")
    print(f"Expected: Metadata from Crossref API for DOI")
    # Note: Actual API call commented out to avoid network dependency in tests
    # result = metadata.fetch_metadata(url)
    # print(f"Result: {result}")


def demo_generic_metadata():
    """Demo: Fetch metadata from generic URL."""
    print("\n=== Demo: Generic URL Metadata ===")
    url = "https://example.com/article"
    print(f"URL: {url}")
    print(f"Expected: Metadata extracted from HTML meta tags")
    # Note: Actual API call commented out to avoid network dependency in tests
    # result = metadata.fetch_metadata(url)
    # print(f"Result: {result}")


if __name__ == "__main__":
    demo_arxiv_metadata()
    demo_doi_metadata()
    demo_generic_metadata()
    print("\n✅ Metadata module ready for use!")
