"""Category management for bibliography."""

import json
from typing import Dict, List, Tuple


def load_categories(file_path: str = "categories.json") -> Dict[str, str]:
    """Load category mappings from file.

    Args:
        file_path: Path to categories JSON file

    Returns:
        Dictionary mapping category ID to category name
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default empty mapping
        return {}


def save_categories(
    categories: Dict[str, str], file_path: str = "categories.json"
) -> None:
    """Save category mappings to file.

    Args:
        categories: Dictionary mapping category ID to category name
        file_path: Path to categories JSON file
    """
    with open(file_path, "w") as f:
        json.dump(categories, f, indent=2, sort_keys=True)


def get_or_create_category(
    name: str, categories: Dict[str, str] = None
) -> Tuple[str, Dict[str, str]]:
    """Get category ID for given name, creating if needed.

    Uses lowercase normalization to group similar categories.

    Args:
        name: Category name
        categories: Existing categories dict (loads from file if not provided)

    Returns:
        Tuple of (category_id, updated_categories_dict)
    """
    if categories is None:
        categories = load_categories()

    # Normalize category name
    normalized = name.lower().strip()

    # Check if category already exists (case-insensitive)
    for cat_id, cat_name in categories.items():
        if cat_name.lower() == normalized:
            return cat_id, categories

    # Create new category
    new_id = str(
        max(int(cat_id) for cat_id in categories.keys() if cat_id.isdigit()) + 1
        if categories
        else 1
    )
    categories[new_id] = name

    return new_id, categories


def list_categories(categories: Dict[str, str] = None) -> List[Tuple[str, str]]:
    """List all categories sorted by ID.

    Args:
        categories: Category mapping dict (loads from file if not provided)

    Returns:
        List of (id, name) tuples sorted by ID
    """
    if categories is None:
        categories = load_categories()

    return sorted(
        categories.items(), key=lambda x: int(x[0]) if x[0].isdigit() else float("inf")
    )


def get_category_name(cat_id: str, categories: Dict[str, str] = None) -> str:
    """Get category name by ID.

    Args:
        cat_id: Category ID
        categories: Category mapping dict (loads from file if not provided)

    Returns:
        Category name, or empty string if not found
    """
    if categories is None:
        categories = load_categories()

    return categories.get(str(cat_id), "")
