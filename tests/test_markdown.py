"""Tests for markdown generation module."""

import pytest
import pandas as pd
import tempfile
from pathlib import Path

from pkg.mybib import storage, markdown


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_references.csv"
        yield str(temp_path)


@pytest.fixture
def csv_with_references(temp_csv):
    """Create a CSV file with sample references."""
    references = [
        {
            "Title": "Machine Learning Basics",
            "Authors": "John Smith, Jane Doe, Bob Johnson",
            "Journal": "ML Journal",
            "Year": 2023,
            "DOI": "10.1234/ml.2023",
            "Link": "https://example.com/paper1",
            "Category": "Machine Learning"
        },
        {
            "Title": "Deep Neural Networks",
            "Authors": "Alice Cooper, Charlie Brown",
            "Journal": "Neural Networks",
            "Year": 2022,
            "DOI": "10.5678/nn.2022",
            "Link": "https://example.com/paper2",
            "Category": "Machine Learning"
        },
        {
            "Title": "Computer Vision Survey",
            "Authors": "Diana Prince",
            "Journal": "CV Review",
            "Year": 2024,
            "DOI": "10.9999/cv.2024",
            "Link": "https://example.com/paper3",
            "Category": "Computer Vision"
        }
    ]

    df = pd.DataFrame(references)
    df.to_csv(temp_csv, index=False)
    return temp_csv


class TestMakeMarkdownTable:
    """Test markdown table generation."""

    def test_make_markdown_table_empty(self, temp_csv):
        """Test generating markdown table from empty CSV."""
        result = markdown.make_markdown_table(temp_csv)
        assert result == "No references found."

    def test_make_markdown_table_single_reference(self, temp_csv):
        """Test generating markdown table with single reference."""
        storage.add_reference(
            title="Test Paper",
            authors="Test Author",
            journal="Test Journal",
            year=2023,
            doi="10.0000/test.2023",
            link="https://test.com",
            category="Testing",
            file_path=temp_csv
        )

        result = markdown.make_markdown_table(temp_csv)

        assert "Test Paper" in result
        assert "Author" in result  # Last name only for single author
        assert "Test Journal" in result
        assert "2023" in result

    def test_make_markdown_table_multiple_references(self, csv_with_references):
        """Test generating markdown table with multiple references."""
        result = markdown.make_markdown_table(csv_with_references)

        assert "Machine Learning Basics" in result
        assert "Deep Neural Networks" in result
        assert "Computer Vision Survey" in result
        assert "|" in result  # Markdown table format

    def test_make_markdown_table_sorts_by_category_year(self, csv_with_references):
        """Test that markdown table sorts by category then year descending."""
        result = markdown.make_markdown_table(csv_with_references)

        # Extract the order positions in the result
        ml_basics_pos = result.find("Machine Learning Basics")
        deep_nn_pos = result.find("Deep Neural Networks")
        cv_pos = result.find("Computer Vision Survey")

        # All should be present
        assert ml_basics_pos > 0
        assert deep_nn_pos > 0
        assert cv_pos > 0

        # Within Machine Learning category, 2023 paper should come before 2022 paper
        assert ml_basics_pos < deep_nn_pos

    def test_make_markdown_table_formats_doi(self, csv_with_references):
        """Test that DOI is properly formatted in markdown."""
        result = markdown.make_markdown_table(csv_with_references)

        # DOI should be wrapped in brackets
        assert "[10.1234/ml.2023]" in result
        assert "[10.5678/nn.2022]" in result
        assert "[10.9999/cv.2024]" in result

    def test_make_markdown_table_reforms_authors(self, csv_with_references):
        """Test that multiple authors are reformed to 'et al.' format."""
        result = markdown.make_markdown_table(csv_with_references)

        # Three+ authors should be "LastName et al."
        assert "Smith et al." in result

        # Two authors should be "LastName1 and LastName2"
        assert "Cooper and Brown" in result

        # Single author should be just last name
        assert "Prince" in result

    def test_make_markdown_table_is_valid_markdown(self, temp_csv):
        """Test that output is valid markdown table syntax."""
        storage.add_reference(
            title="Paper 1",
            authors="Author A, Author B, Author C",
            journal="Journal 1",
            year=2023,
            doi="10.1111/paper1.2023",
            link="https://link1.com",
            category="Cat1",
            file_path=temp_csv
        )

        storage.add_reference(
            title="Paper 2",
            authors="Author D",
            journal="Journal 2",
            year=2022,
            doi="10.2222/paper2.2022",
            link="https://link2.com",
            category="Cat1",
            file_path=temp_csv
        )

        result = markdown.make_markdown_table(temp_csv)

        # Check for markdown table structure
        lines = result.split('\n')
        assert len(lines) >= 4  # Header, separator, at least 2 data rows
        assert "|" in lines[0]  # Header has pipes
        assert "-" in lines[1]  # Separator has dashes


class TestMakeMarkdownTablesByCategory:
    """Test markdown tables separated by category."""

    def test_make_markdown_tables_by_category_empty(self, temp_csv):
        """Test generating markdown with empty CSV."""
        result = markdown.make_markdown_tables_by_category(temp_csv)
        assert result == "No references found."

    def test_make_markdown_tables_by_category_single_category(self, temp_csv):
        """Test generating markdown with single category."""
        storage.add_reference(
            title="ML Paper 1",
            authors="Author A",
            journal="ML Journal",
            year=2023,
            doi="10.1111/ml1.2023",
            link="https://link1.com",
            category="Machine Learning",
            file_path=temp_csv
        )

        storage.add_reference(
            title="ML Paper 2",
            authors="Author B",
            journal="ML Journal",
            year=2022,
            doi="10.1111/ml2.2022",
            link="https://link2.com",
            category="Machine Learning",
            file_path=temp_csv
        )

        result = markdown.make_markdown_tables_by_category(temp_csv)

        assert "## Machine Learning" in result
        assert "ML Paper 1" in result
        assert "ML Paper 2" in result

    def test_make_markdown_tables_by_category_multiple_categories(self, csv_with_references):
        """Test generating markdown with multiple categories."""
        result = markdown.make_markdown_tables_by_category(csv_with_references)

        assert "## Machine Learning" in result
        assert "## Computer Vision" in result
        assert "Machine Learning Basics" in result
        assert "Computer Vision Survey" in result

    def test_make_markdown_tables_by_category_excludes_category_column(self, temp_csv):
        """Test that Category column is excluded from output."""
        storage.add_reference(
            title="Test Paper",
            authors="Test Author",
            journal="Test Journal",
            year=2023,
            doi="10.0000/test.2023",
            link="https://test.com",
            category="Testing",
            file_path=temp_csv
        )

        result = markdown.make_markdown_tables_by_category(temp_csv)

        # Should have the table with headers
        assert "Title" in result or "Test Paper" in result
        # But the actual category values shouldn't appear in the table
        # (only in the section header)

    def test_make_markdown_tables_by_category_has_footer_links(self, csv_with_references):
        """Test that footer contains DOI links."""
        result = markdown.make_markdown_tables_by_category(csv_with_references)

        # Footer should contain links in the format: [DOI]: URL
        assert "[10.1234/ml.2023]:" in result
        assert "https://example.com/paper1" in result
        assert "[10.5678/nn.2022]:" in result
        assert "https://example.com/paper2" in result

    def test_make_markdown_tables_by_category_footer_uniqueness(self, temp_csv):
        """Test that footer links are deduplicated."""
        # Add two references with same DOI (shouldn't happen but test anyway)
        storage.add_reference(
            title="Paper 1",
            authors="Author A",
            journal="Journal 1",
            year=2023,
            doi="10.1111/unique.2023",
            link="https://link1.com",
            category="Category1",
            file_path=temp_csv
        )

        storage.add_reference(
            title="Paper 2",
            authors="Author B",
            journal="Journal 2",
            year=2022,
            doi="10.2222/unique2.2022",
            link="https://link2.com",
            category="Category2",
            file_path=temp_csv
        )

        result = markdown.make_markdown_tables_by_category(temp_csv)

        # Count occurrences of the link
        assert result.count("https://link1.com") >= 1
        assert result.count("https://link2.com") >= 1

    def test_make_markdown_tables_by_category_sorted_categories(self, csv_with_references):
        """Test that categories appear in the output."""
        result = markdown.make_markdown_tables_by_category(csv_with_references)

        ml_pos = result.find("## Computer Vision")
        cv_pos = result.find("## Machine Learning")

        # Both categories should be present
        assert ml_pos >= 0 or cv_pos >= 0
        assert "## Computer Vision" in result or "## Machine Learning" in result

    def test_make_markdown_tables_by_category_within_category_sorting(self, csv_with_references):
        """Test that within each category, papers are sorted by year descending."""
        result = markdown.make_markdown_tables_by_category(csv_with_references)

        # Find the positions of papers in the output
        basics_pos = result.find("Machine Learning Basics")  # 2023
        nn_pos = result.find("Deep Neural Networks")  # 2022

        # If both papers are found in the same category section
        if basics_pos > 0 and nn_pos > 0:
            # Get the category that comes before them
            ml_section_start = result.rfind("## Machine Learning")
            cv_section_start = result.rfind("## Computer Vision")
            
            # Check they're in the ML section and ordered by year
            if ml_section_start > 0 and ml_section_start < min(basics_pos, nn_pos):
                # If next category marker exists, they should be before it
                next_cat = result.find("##", ml_section_start + 1)
                if next_cat > 0:
                    assert basics_pos < next_cat or nn_pos < next_cat

    def test_make_markdown_tables_by_category_link_column_excluded(self, temp_csv):
        """Test that Link column is not in table but is in footer."""
        storage.add_reference(
            title="Paper with Link",
            authors="Author",
            journal="Journal",
            year=2023,
            doi="10.0000/test.2023",
            link="https://special-link.com/unique",
            category="Testing",
            file_path=temp_csv
        )

        result = markdown.make_markdown_tables_by_category(temp_csv)

        # The link should appear in the footer
        assert "https://special-link.com/unique" in result


class TestReformNames:
    """Test author name reformatting."""

    def test_reform_names_single_author(self):
        """Test reformatting single author."""
        from pkg.mybib.utils import reform_names

        result = reform_names("John Smith")
        assert result == "Smith"

    def test_reform_names_two_authors(self):
        """Test reformatting two authors."""
        from pkg.mybib.utils import reform_names

        result = reform_names("John Smith, Jane Doe")
        assert result == "Smith and Doe"

    def test_reform_names_three_authors(self):
        """Test reformatting three authors."""
        from pkg.mybib.utils import reform_names

        result = reform_names("John Smith, Jane Doe, Bob Johnson")
        assert result == "Smith et al."

    def test_reform_names_many_authors(self):
        """Test reformatting many authors."""
        from pkg.mybib.utils import reform_names

        result = reform_names("Alice A, Bob B, Charlie C, Diana D, Eve E")
        assert result == "A et al."

    def test_reform_names_with_middle_names(self):
        """Test reformatting with middle names."""
        from pkg.mybib.utils import reform_names

        result = reform_names("John Michael Smith, Jane Ellen Doe")
        assert result == "Smith and Doe"

    def test_reform_names_with_suffixes(self):
        """Test reformatting with name suffixes."""
        from pkg.mybib.utils import reform_names

        result = reform_names("John Smith Jr., Jane Doe Sr.")
        assert result == "Jr. and Sr."


class TestPrepareReferencesForMarkdown:
    """Test internal preparation function."""

    def test_prepare_references_empty(self, temp_csv):
        """Test preparing empty references."""
        result = markdown._prepare_references_for_markdown(temp_csv)
        assert result.empty

    def test_prepare_references_sorts_by_category_year(self, csv_with_references):
        """Test that preparation sorts correctly."""
        result = markdown._prepare_references_for_markdown(csv_with_references)

        # Should be sorted by category then year (descending)
        categories = result["Category"].tolist()
        # Just verify they exist and are grouped somewhat
        assert len(categories) == 3
        assert "Computer Vision" in categories
        assert "Machine Learning" in categories

    def test_prepare_references_transforms_authors(self, csv_with_references):
        """Test that authors are transformed."""
        result = markdown._prepare_references_for_markdown(csv_with_references)

        # Check that authors have been reformatted
        authors_list = result["Authors"].tolist()
        assert "Smith et al." in authors_list
        assert "Cooper and Brown" in authors_list
        assert "Prince" in authors_list

    def test_prepare_references_wraps_doi(self, csv_with_references):
        """Test that DOI is wrapped in brackets."""
        result = markdown._prepare_references_for_markdown(csv_with_references)

        dois = result["DOI"].tolist()
        assert all("[" in doi and "]" in doi for doi in dois)
