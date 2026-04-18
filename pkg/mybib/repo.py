"""Fetch metadata for Git repositories hosted on GitHub and Hugging Face."""

import re
import sys
from urllib.parse import urlparse

import requests


def fetch_repo_metadata(repo_url: str) -> dict:
    """Fetch metadata for a supported repository URL.

    Args:
        repo_url: Repository URL on github.com or huggingface.co

    Returns:
        Dictionary with keys: title, authors, journal, year, doi, link, repo_id

    Raises:
        SystemExit: If URL is unsupported or metadata cannot be fetched
    """
    source, repo_id, repo_kind = _parse_repo_url(repo_url)

    if source == "github":
        return _fetch_github_metadata(repo_id)

    return _fetch_huggingface_metadata(repo_id, repo_kind)


def _parse_repo_url(repo_url: str) -> tuple[str, str, str]:
    """Parse repository URL and return source-specific metadata.

    Returns:
        (source, repo_id, repo_kind)
        - source: "github" or "huggingface"
        - repo_id: owner/repo or namespace/repo
        - repo_kind: "repo" for GitHub, and "model"/"dataset"/"space" for HF
    """
    parsed = urlparse(repo_url.strip())

    host = parsed.netloc.lower().replace("www.", "")
    path = parsed.path.strip("/")

    if host == "github.com":
        return _parse_github_repo(path)

    if host == "huggingface.co":
        return _parse_huggingface_repo(path)

    print("Unsupported repository URL. Use github.com or huggingface.co URLs.")
    sys.exit(1)


def _parse_github_repo(path: str) -> tuple[str, str, str]:
    """Parse a GitHub repository path to owner/repo format."""
    normalized = re.sub(r"\.git$", "", path)
    parts = [part for part in normalized.split("/") if part]

    if len(parts) < 2:
        print("Invalid GitHub repository URL. Expected format: github.com/owner/repo")
        sys.exit(1)

    repo_id = f"{parts[0]}/{parts[1]}"
    return "github", repo_id, "repo"


def _parse_huggingface_repo(path: str) -> tuple[str, str, str]:
    """Parse a Hugging Face repository path.

    Supported URLs:
    - huggingface.co/<namespace>/<repo> (model)
    - huggingface.co/datasets/<namespace>/<repo>
    - huggingface.co/spaces/<namespace>/<repo>
    """
    parts = [part for part in path.split("/") if part]

    if not parts:
        print("Invalid Hugging Face repository URL.")
        sys.exit(1)

    kind = "model"
    start_index = 0

    if parts[0] in {"datasets", "spaces"}:
        kind = "dataset" if parts[0] == "datasets" else "space"
        start_index = 1

    if len(parts) - start_index < 2:
        print(
            "Invalid Hugging Face repository URL. "
            "Expected format: huggingface.co/<namespace>/<repo>"
        )
        sys.exit(1)

    repo_id = f"{parts[start_index]}/{parts[start_index + 1]}"
    return "huggingface", repo_id, kind


def _fetch_github_metadata(repo_id: str) -> dict:
    """Fetch repository metadata from GitHub API."""
    url = f"https://api.github.com/repos/{repo_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Error fetching GitHub metadata: {exc}")
        sys.exit(1)

    data = response.json()

    created_at = data.get("created_at")
    year = int(created_at[:4]) if created_at else None

    full_name = data.get("full_name", repo_id)
    owner = (data.get("owner") or {}).get("login") or repo_id.split("/")[0]
    link = data.get("html_url", f"https://github.com/{repo_id}")

    return {
        "title": full_name,
        "authors": owner,
        "journal": "GitHub",
        "year": year,
        "doi": f"github:{full_name.lower()}",
        "link": link,
        "repo_id": full_name,
    }


def _fetch_huggingface_metadata(repo_id: str, repo_kind: str) -> dict:
    """Fetch repository metadata from Hugging Face Hub API."""
    if repo_kind == "dataset":
        api_url = f"https://huggingface.co/api/datasets/{repo_id}"
        page_url = f"https://huggingface.co/datasets/{repo_id}"
        journal = "Hugging Face Datasets"
    elif repo_kind == "space":
        api_url = f"https://huggingface.co/api/spaces/{repo_id}"
        page_url = f"https://huggingface.co/spaces/{repo_id}"
        journal = "Hugging Face Spaces"
    else:
        api_url = f"https://huggingface.co/api/models/{repo_id}"
        page_url = f"https://huggingface.co/{repo_id}"
        journal = "Hugging Face"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Error fetching Hugging Face metadata: {exc}")
        sys.exit(1)

    data = response.json()

    created_at = (
        data.get("createdAt")
        or data.get("created_at")
        or data.get("lastModified")
        or data.get("last_modified")
    )
    year = int(created_at[:4]) if created_at else None

    title = data.get("id") or repo_id
    author = data.get("author") or repo_id.split("/")[0]
    link = data.get("url") or page_url

    return {
        "title": title,
        "authors": author,
        "journal": journal,
        "year": year,
        "doi": f"huggingface:{repo_kind}:{title.lower()}",
        "link": link,
        "repo_id": title,
    }
