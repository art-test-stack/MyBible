"""Tests for CLI command parsing and dispatch."""

import sys
from unittest.mock import patch

import pytest

from pkg.mybib import cli


class TestAddRepoCommand:
    """Test add-repo CLI command behavior."""

    def test_add_repo_dispatches_to_handler(self):
        """The add-repo command should dispatch to handle_add_repo."""
        argv = ["mybib", "add-repo", "https://github.com/openai/whisper"]

        with patch.object(sys, "argv", argv):
            with patch("pkg.mybib.cli.handle_add_repo") as mock_handler:
                cli.main()

        mock_handler.assert_called_once()
        parsed_args = mock_handler.call_args[0][0]
        assert parsed_args.command == "add-repo"
        assert parsed_args.repo_url == "https://github.com/openai/whisper"
        assert parsed_args.file == "references.csv"

    def test_add_repo_requires_repo_url(self):
        """The add-repo command should require a repository URL argument."""
        argv = ["mybib", "add-repo"]

        with patch.object(sys, "argv", argv):
            with pytest.raises(SystemExit):
                cli.main()
