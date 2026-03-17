"""Generate markdown tables from reference data."""

from .storage import load_references
from .utils import reform_names


def _prepare_references_for_markdown(file_path: str = "references.csv"):
    """Prepare references DataFrame for markdown output.

    Args:
        file_path: Path to the CSV file

    Returns:
        Processed DataFrame ready for markdown conversion
    """
    df = load_references(file_path)

    if df.empty:
        return df

    df["Authors"] = df["Authors"].apply(reform_names)
    df["DOI"] = df.apply(lambda row: f"[{row.get('DOI', 'unknown')}]", axis=1)
    df = df.sort_values(by=["Category", "Year"], ascending=[True, False])

    return df


def make_markdown_table(file_path: str = "references.csv") -> str:
    """Generate a markdown table from all references.

    Args:
        file_path: Path to the CSV file

    Returns:
        Markdown formatted table as string
    """
    df = _prepare_references_for_markdown(file_path)

    if df.empty:
        return "No references found."

    markdown_table = df.to_markdown(index=False)
    return markdown_table


def make_markdown_tables_by_category(file_path: str = "references.csv") -> str:
    """Generate markdown tables separated by category.

    Args:
        file_path: Path to the CSV file

    Returns:
        Markdown formatted tables with category headers and footer links
    """
    df = _prepare_references_for_markdown(file_path)

    if df.empty:
        return "No references found."

    output = []
    footer = []

    for category, group in df.groupby("Category"):
        output.append(f"## {category}\n")
        table = group.drop(columns=["Category", "Link"]).to_markdown(index=False)
        output.append(table)
        output.append("\n")

        # Collect footer links
        footer.extend(
            f"{doi}: {link}" for doi, link in zip(group["DOI"], group["Link"])
        )

    # Sort and deduplicate footer
    footer = sorted(set(footer), key=lambda x: x.split(":")[0])

    return "\n".join(output) + "\n".join(footer)
