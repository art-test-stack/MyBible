"""Utility functions for bibliography management."""


def reform_names(authors_str: str) -> str:
    """Format author names for display.
    
    Converts full author lists to abbreviated form:
    - Single author: Last name only
    - Two authors: "LastName1 and LastName2"
    - Three+ authors: "LastName et al."
    
    Args:
        authors_str: Comma-separated string of author names
        
    Returns:
        Formatted author string
    """
    authors = authors_str.split(", ")
    
    if len(authors) > 2:
        first_author_last_name = authors[0].split()[-1]
        return f"{first_author_last_name} et al."
    elif len(authors) == 2:
        first_author_last_name = authors[0].split()[-1]
        second_author_last_name = authors[1].split()[-1]
        return f"{first_author_last_name} and {second_author_last_name}"
    else:
        return authors[0].split()[-1]
