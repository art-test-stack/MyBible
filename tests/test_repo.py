"""Tests for repository metadata fetching module."""

from unittest.mock import Mock, patch

import pytest
import requests

from pkg.mybib import repo


class TestParseRepoUrl:
    """Test repository URL parsing."""

    def test_parse_github_url(self):
        """Parse a GitHub repository URL."""
        source, repo_id, repo_kind = repo._parse_repo_url(
            "https://github.com/openai/whisper"
        )

        assert source == "github"
        assert repo_id == "openai/whisper"
        assert repo_kind == "repo"

    def test_parse_huggingface_model_url(self):
        """Parse a Hugging Face model URL."""
        source, repo_id, repo_kind = repo._parse_repo_url(
            "https://huggingface.co/google/gemma-2-2b"
        )

        assert source == "huggingface"
        assert repo_id == "google/gemma-2-2b"
        assert repo_kind == "model"

    def test_parse_huggingface_dataset_url(self):
        """Parse a Hugging Face dataset URL."""
        source, repo_id, repo_kind = repo._parse_repo_url(
            "https://huggingface.co/datasets/HuggingFaceFW/fineweb"
        )

        assert source == "huggingface"
        assert repo_id == "HuggingFaceFW/fineweb"
        assert repo_kind == "dataset"

    @patch("pkg.mybib.repo.sys.exit", side_effect=SystemExit)
    def test_parse_unsupported_host(self, _mock_exit):
        """Unsupported hosts should trigger a clean exit."""
        with pytest.raises(SystemExit):
            repo._parse_repo_url("https://gitlab.com/group/project")


class TestFetchRepoMetadata:
    """Test metadata fetching from supported providers."""

    @patch("pkg.mybib.repo.requests.get")
    def test_fetch_github_metadata(self, mock_get):
        """Fetch metadata from GitHub API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "full_name": "openai/whisper",
            "owner": {"login": "openai"},
            "created_at": "2022-09-21T00:00:00Z",
            "html_url": "https://github.com/openai/whisper",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = repo.fetch_repo_metadata("https://github.com/openai/whisper")

        assert result["title"] == "openai/whisper"
        assert result["authors"] == "openai"
        assert result["journal"] == "GitHub"
        assert result["year"] == 2022
        assert result["doi"] == "github:openai/whisper"
        assert result["link"] == "https://github.com/openai/whisper"

    @patch("pkg.mybib.repo.requests.get")
    def test_fetch_huggingface_model_metadata(self, mock_get):
        """Fetch metadata from Hugging Face model API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "google/gemma-2-2b",
            "author": "google",
            "createdAt": "2024-06-27T00:00:00Z",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = repo.fetch_repo_metadata("https://huggingface.co/google/gemma-2-2b")

        assert result["title"] == "google/gemma-2-2b"
        assert result["authors"] == "google"
        assert result["journal"] == "Hugging Face"
        assert result["year"] == 2024
        assert result["doi"] == "huggingface:model:google/gemma-2-2b"
        assert result["link"] == "https://huggingface.co/google/gemma-2-2b"

    @patch("pkg.mybib.repo.requests.get")
    def test_fetch_huggingface_dataset_metadata(self, mock_get):
        """Fetch metadata from Hugging Face dataset API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "HuggingFaceFW/fineweb",
            "author": "HuggingFaceFW",
            "lastModified": "2025-01-10T00:00:00Z",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = repo.fetch_repo_metadata(
            "https://huggingface.co/datasets/HuggingFaceFW/fineweb"
        )

        assert result["title"] == "HuggingFaceFW/fineweb"
        assert result["authors"] == "HuggingFaceFW"
        assert result["journal"] == "Hugging Face Datasets"
        assert result["year"] == 2025
        assert result["doi"] == "huggingface:dataset:huggingfacefw/fineweb"
        assert result["link"] == "https://huggingface.co/datasets/HuggingFaceFW/fineweb"

    @patch("pkg.mybib.repo.sys.exit", side_effect=SystemExit)
    @patch("pkg.mybib.repo.requests.get")
    def test_fetch_repo_metadata_api_failure(self, mock_get, _mock_exit):
        """API failures should trigger a clean exit."""
        mock_get.side_effect = requests.RequestException("network failure")

        with pytest.raises(SystemExit):
            repo.fetch_repo_metadata("https://github.com/openai/whisper")
