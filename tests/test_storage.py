"""Tests for storage module."""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys

from pkg.mybib import storage


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    # Delete the empty file so it can be created fresh
    Path(temp_path).unlink(missing_ok=True)
    yield temp_path
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def sample_references():
    """Sample reference data for testing."""
    return {
        "title": "Machine Learning Basics",
        "authors": "John Smith, Jane Doe",
        "journal": "Neural Networks",
        "year": 2023,
        "doi": "10.1234/example.2023",
        "link": "https://example.com/paper1",
        "category": "Machine Learning"
    }


class TestAddReference:
    """Test adding references to storage."""

    def test_add_reference_to_empty_file(self, temp_csv, sample_references):
        """Test adding a reference to a new CSV file."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        df = pd.read_csv(temp_csv)
        assert len(df) == 1
        assert df.iloc[0]["Title"] == sample_references["title"]
        assert df.iloc[0]["DOI"] == sample_references["doi"]

    def test_add_multiple_references(self, temp_csv, sample_references):
        """Test adding multiple references."""
        # Add first reference
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        # Add second reference
        storage.add_reference(
            title="Deep Learning Advanced",
            authors="Alice Johnson, Bob Wilson",
            journal="AI Journal",
            year=2024,
            doi="10.5678/example.2024",
            link="https://example.com/paper2",
            category="Deep Learning",
            file_path=temp_csv
        )

        df = pd.read_csv(temp_csv)
        assert len(df) == 2
        assert df.iloc[0]["DOI"] == sample_references["doi"]
        assert df.iloc[1]["DOI"] == "10.5678/example.2024"

    def test_add_reference_preserves_headers(self, temp_csv, sample_references):
        """Test that adding references preserves CSV headers."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        storage.add_reference(
            title="Another Paper",
            authors="Charlie Brown",
            journal="Tech Review",
            year=2022,
            doi="10.9999/another.2022",
            link="https://example.com/paper3",
            category="Research",
            file_path=temp_csv
        )

        df = pd.read_csv(temp_csv)
        # Check headers are correct
        expected_headers = ["Title", "Authors", "Journal", "Year", "DOI", "Link", "Category"]
        assert list(df.columns) == expected_headers


class TestDuplicateDetection:
    """Test duplicate reference detection."""

    def test_duplicate_doi_detection(self, temp_csv, sample_references):
        """Test that adding a reference with duplicate DOI is rejected."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        # Try to add duplicate with different title
        with patch('sys.exit') as mock_exit:
            storage.add_reference(
                title="Different Title",
                authors="Different Authors",
                journal="Different Journal",
                year=2025,
                doi=sample_references["doi"],  # Same DOI
                link="https://different.com",
                category="Different Category",
                file_path=temp_csv
            )
            mock_exit.assert_called_once_with(0)

    def test_duplicate_detection_case_insensitive(self, temp_csv, sample_references):
        """Test that duplicate detection is case-insensitive."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        # Try to add duplicate with different case DOI
        with patch('sys.exit') as mock_exit:
            storage.add_reference(
                title="Another Title",
                authors="Another Author",
                journal="Another Journal",
                year=2024,
                doi=sample_references["doi"].upper(),  # Different case
                link="https://another.com",
                category="Another Category",
                file_path=temp_csv
            )
            mock_exit.assert_called_once_with(0)

    def test_duplicate_detection_with_whitespace(self, temp_csv, sample_references):
        """Test that duplicate detection ignores whitespace."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        # Try to add duplicate with extra whitespace
        with patch('sys.exit') as mock_exit:
            storage.add_reference(
                title="Yet Another Title",
                authors="Yet Another Author",
                journal="Yet Another Journal",
                year=2025,
                doi=f"  {sample_references['doi']}  ",  # Whitespace added
                link="https://yet-another.com",
                category="Yet Another Category",
                file_path=temp_csv
            )
            mock_exit.assert_called_once_with(0)

    def test_no_duplicate_with_different_doi(self, temp_csv, sample_references):
        """Test that different DOIs are not flagged as duplicates."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        # Add reference with different DOI
        storage.add_reference(
            title="Another Paper",
            authors="Another Author",
            journal="Another Journal",
            year=2024,
            doi="10.1111/different.2024",  # Different DOI
            link="https://another.com",
            category="Different Category",
            file_path=temp_csv
        )

        df = pd.read_csv(temp_csv)
        assert len(df) == 2


class TestLoadReferences:
    """Test loading references from storage."""

    def test_load_references_from_existing_file(self, temp_csv, sample_references):
        """Test loading references from an existing CSV file."""
        storage.add_reference(
            title=sample_references["title"],
            authors=sample_references["authors"],
            journal=sample_references["journal"],
            year=sample_references["year"],
            doi=sample_references["doi"],
            link=sample_references["link"],
            category=sample_references["category"],
            file_path=temp_csv
        )

        df = storage.load_references(temp_csv)
        assert len(df) == 1
        assert df.iloc[0]["Title"] == sample_references["title"]

    def test_load_references_creates_empty_file(self, temp_csv):
        """Test that loading from non-existent file creates empty structure."""
        # Remove the temp file
        Path(temp_csv).unlink(missing_ok=True)

        df = storage.load_references(temp_csv)
        
        assert df.empty
        assert list(df.columns) == ["Title", "Authors", "Journal", "Year", "DOI", "Link", "Category"]
        assert Path(temp_csv).exists()

    def test_load_references_preserves_data(self, temp_csv, sample_references):
        """Test that loading preserves all reference data."""
        # Add multiple references
        for i in range(3):
            storage.add_reference(
                title=f"Paper {i}",
                authors=f"Author {i}",
                journal=f"Journal {i}",
                year=2020 + i,
                doi=f"10.{i}/example.{2020+i}",
                link=f"https://example.com/paper{i}",
                category=f"Category {i}",
                file_path=temp_csv
            )

        df = storage.load_references(temp_csv)
        assert len(df) == 3
        assert df["Year"].tolist() == [2020, 2021, 2022]
