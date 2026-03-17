"""Utility functions for bibliography management."""


def reform_names(authors_str: str) -> str:
    """Format author names for display.

    Converts full author lists to abbreviated form:
    - Single author or team: Last name only
    - Two authors: "LastName1 and LastName2"
    - Three+ authors: "FirstAuthor et al."
    - Team names (contain "Team"): Entity name only without "et al."

    Args:
        authors_str: Comma-separated string of author names or "Authors et al." format

    Returns:
        Formatted author string
    """
    if not authors_str or not isinstance(authors_str, str):
        return ""

    authors_str = authors_str.strip()

    # Handle "X et al." format - extract just the first author
    if " et al." in authors_str:
        first_author = authors_str.split(" et al.")[0].strip()
        # Extract last name from first author
        first_author_last = first_author.split()[-1]
        return f"{first_author_last} et al."

    # Check if it's a team name (contains "Team", "AI", etc.)
    if any(
        team_keyword in authors_str
        for team_keyword in [
            "Team",
            "team",
            "-Ai",
            "Mistral",
            "Meta",
            "OpenAI",
            "DeepMind",
            "Google",
        ]
    ):
        # Just return the entity name as is, or extract last part
        parts = authors_str.split(",")
        if len(parts) > 0:
            return parts[0].strip()
        return authors_str

    # Split by comma
    authors = [a.strip() for a in authors_str.split(",")]

    if len(authors) > 2:
        first_author_last_name = authors[0].split()[-1]
        return f"{first_author_last_name} et al."
    elif len(authors) == 2:
        first_author_last_name = authors[0].split()[-1]
        second_author_last_name = authors[1].split()[-1]
        return f"{first_author_last_name} and {second_author_last_name}"
    else:
        return authors[0].split()[-1] if authors[0] else ""
