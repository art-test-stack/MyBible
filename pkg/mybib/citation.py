"""Fetch citation BibTeX from arXiv and repository pages."""

import base64
import html
import re
from urllib.parse import urlparse

import requests


def fetch_arxiv_bibtex(arxiv_id: str) -> str | None:
    """Fetch BibTeX citation for an arXiv paper ID."""
    if not arxiv_id:
        return None

    url = f"https://arxiv.org/bibtex/{arxiv_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    text = html.unescape(response.text)
    return _extract_first_bibtex_entry(text)


def fetch_repo_bibtex(repo_url: str) -> str | None:
    """Fetch BibTeX citation from a repository README."""
    source_info = _parse_supported_repo_url(repo_url)
    if source_info is None:
        return None

    source = source_info["source"]
    if source == "github":
        markdown = _fetch_github_readme(source_info["repo_id"])
    else:
        markdown = _fetch_huggingface_readme(
            source_info["repo_id"], source_info["repo_kind"]
        )

    if not markdown:
        return None

    return _extract_bibtex_from_markdown(markdown)


def fetch_bibtex_for_row(arxiv_id: str = None, link: str = None, doi: str = None) -> str | None:
    """Fetch BibTeX for an existing reference row using available identifiers."""
    normalized_arxiv = _normalized_text(arxiv_id)
    normalized_link = _normalized_text(link)
    normalized_doi = _normalized_text(doi)

    if normalized_arxiv:
        bib = fetch_arxiv_bibtex(normalized_arxiv)
        if bib:
            return bib

    if normalized_link:
        parsed = urlparse(normalized_link)
        host = parsed.netloc.lower().replace("www.", "")
        if host == "arxiv.org":
            extracted = _extract_arxiv_id_from_link(normalized_link)
            if extracted:
                bib = fetch_arxiv_bibtex(extracted)
                if bib:
                    return bib
        if host in {"github.com", "huggingface.co"}:
            bib = fetch_repo_bibtex(normalized_link)
            if bib:
                return bib

    if normalized_doi.startswith("github:"):
        repo_id = normalized_doi.split("github:", 1)[1]
        return fetch_repo_bibtex(f"https://github.com/{repo_id}")

    if normalized_doi.startswith("huggingface:"):
        parts = normalized_doi.split(":", 2)
        if len(parts) == 3:
            repo_kind = parts[1]
            repo_id = parts[2]
            if repo_kind == "dataset":
                return fetch_repo_bibtex(f"https://huggingface.co/datasets/{repo_id}")
            if repo_kind == "space":
                return fetch_repo_bibtex(f"https://huggingface.co/spaces/{repo_id}")
            return fetch_repo_bibtex(f"https://huggingface.co/{repo_id}")

    return None


def _parse_supported_repo_url(repo_url: str) -> dict | None:
    parsed = urlparse((repo_url or "").strip())
    host = parsed.netloc.lower().replace("www.", "")
    path = parsed.path.strip("/")
    parts = [part for part in path.split("/") if part]

    if host == "github.com":
        if len(parts) < 2:
            return None
        repo_id = f"{parts[0]}/{parts[1].removesuffix('.git')}"
        return {"source": "github", "repo_id": repo_id, "repo_kind": "repo"}

    if host == "huggingface.co":
        if not parts:
            return None
        repo_kind = "model"
        start = 0
        if parts[0] in {"datasets", "spaces"}:
            repo_kind = "dataset" if parts[0] == "datasets" else "space"
            start = 1
        if len(parts) - start < 2:
            return None
        repo_id = f"{parts[start]}/{parts[start + 1]}"
        return {"source": "huggingface", "repo_id": repo_id, "repo_kind": repo_kind}

    return None


def _fetch_github_readme(repo_id: str) -> str | None:
    url = f"https://api.github.com/repos/{repo_id}/readme"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    data = response.json()
    encoded = data.get("content")
    if not encoded:
        return None

    try:
        normalized = encoded.replace("\n", "")
        return base64.b64decode(normalized).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _fetch_huggingface_readme(repo_id: str, repo_kind: str) -> str | None:
    if repo_kind == "dataset":
        url = f"https://huggingface.co/datasets/{repo_id}/resolve/main/README.md"
    elif repo_kind == "space":
        url = f"https://huggingface.co/spaces/{repo_id}/resolve/main/README.md"
    else:
        url = f"https://huggingface.co/{repo_id}/resolve/main/README.md"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    return response.text


def _extract_bibtex_from_markdown(markdown_text: str) -> str | None:
    fenced_pattern = re.compile(
        r"```(?:bibtex|bib|BibTeX|BIBTEX)\s*(.*?)```",
        re.DOTALL,
    )
    for match in fenced_pattern.finditer(markdown_text):
        candidate = _extract_first_bibtex_entry(match.group(1))
        if candidate:
            return candidate

    return _extract_first_bibtex_entry(markdown_text)


def _extract_first_bibtex_entry(text: str) -> str | None:
    clean_text = re.sub(r"<[^>]+>", "", text)
    at_index = clean_text.find("@")
    if at_index == -1:
        return None

    brace_start = clean_text.find("{", at_index)
    if brace_start == -1:
        return None

    depth = 0
    end_index = None
    for idx in range(brace_start, len(clean_text)):
        char = clean_text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_index = idx
                break

    if end_index is None:
        return None

    return clean_text[at_index : end_index + 1].strip()


def _normalized_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    return text


def _extract_arxiv_id_from_link(link: str) -> str | None:
    match = re.search(r"/abs/(\d{4}\.\d{4,5}(?:v\d+)?)", link)
    if match:
        return match.group(1).split("v", 1)[0]

    match = re.search(r"/pdf/(\d{4}\.\d{4,5}(?:v\d+)?)", link)
    if match:
        return match.group(1).split("v", 1)[0]

    return None
