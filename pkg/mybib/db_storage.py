"""Database storage adapter for bibliography management."""

from typing import Optional, List, Dict
from sqlalchemy.exc import IntegrityError
from .models import Reference, Category, create_db_engine, init_db, get_session


class DatabaseStorage:
    """Database storage adapter for references and categories."""

    def __init__(self, db_url: str = "sqlite:///bibliography.db"):
        """Initialize database storage.
        
        Args:
            db_url: Database connection URL
        """
        self.engine = create_db_engine(db_url)
        init_db(self.engine)

    def add_reference(
        self,
        title: str,
        authors: str = None,
        journal: str = None,
        year: int = None,
        doi: str = None,
        link: str = None,
        category_name: str = None,
        arxiv_id: str = None,
        scholar_id: str = None,
    ) -> Optional[Reference]:
        """Add a reference to the database.
        
        Args:
            title: Article title
            authors: Comma-separated author names
            journal: Journal/publication name
            year: Publication year
            doi: DOI identifier
            link: URL link
            category_name: Category name
            arxiv_id: arXiv identifier
            scholar_id: Google Scholar ID
            
        Returns:
            Created Reference object or None if duplicate
        """
        session = get_session(self.engine)
        
        try:
            # Check for duplicate DOI
            if doi:
                existing = session.query(Reference).filter_by(doi=doi).first()
                if existing:
                    session.close()
                    return None
            
            # Get or create category
            category = None
            if category_name:
                category = session.query(Category).filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name)
                    session.add(category)
                    session.flush()
            
            # Create reference
            reference = Reference(
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                doi=doi or scholar_id,  # Use scholar_id as DOI fallback
                link=link,
                arxiv_id=arxiv_id,
                scholar_id=scholar_id,
                category_id=category.id if category else None,
            )
            
            session.add(reference)
            session.commit()
            session.close()
            
            return reference
            
        except IntegrityError:
            session.rollback()
            session.close()
            return None
        except Exception as e:
            session.rollback()
            session.close()
            raise e

    def get_references(
        self, category_id: int = None, year: int = None, order_by: str = None
    ) -> List[Reference]:
        """Get references from database with optional filtering.
        
        Args:
            category_id: Filter by category ID
            year: Filter by year
            order_by: Field to order by (e.g., "year", "-year", "title")
            
        Returns:
            List of Reference objects
        """
        session = get_session(self.engine)
        query = session.query(Reference)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if year:
            query = query.filter_by(year=year)
        
        # Ordering
        if order_by:
            reverse = order_by.startswith("-")
            field = order_by[1:] if reverse else order_by
            
            if hasattr(Reference, field):
                col = getattr(Reference, field)
                query = query.order_by(col.desc() if reverse else col)
        else:
            # Default ordering: category, then year descending
            query = query.order_by(Category.name, Reference.year.desc())
        
        results = query.all()
        session.close()
        
        return results

    def add_category(self, name: str, description: str = None) -> Optional[Category]:
        """Add a category to the database.
        
        Args:
            name: Category name
            description: Optional description
            
        Returns:
            Created Category object or None if duplicate
        """
        session = get_session(self.engine)
        
        try:
            # Check for existing category (case-insensitive)
            existing = (
                session.query(Category)
                .filter(Category.name.ilike(name))
                .first()
            )
            
            if existing:
                session.close()
                return existing
            
            category = Category(name=name, description=description)
            session.add(category)
            session.commit()
            session.close()
            
            return category
            
        except IntegrityError:
            session.rollback()
            session.close()
            return None
        except Exception as e:
            session.rollback()
            session.close()
            raise e

    def get_categories(self) -> List[Category]:
        """Get all categories.
        
        Returns:
            List of Category objects ordered by name
        """
        session = get_session(self.engine)
        categories = session.query(Category).order_by(Category.name).all()
        session.close()
        
        return categories

    def migrate_from_csv(self, csv_file: str) -> Dict[str, int]:
        """Migrate references from CSV file to database.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            Dictionary with migration statistics
        """
        import pandas as pd
        
        df = pd.read_csv(csv_file, dtype={"ArxivID": str})
        df = df.fillna("")
        
        stats = {
            "total": len(df),
            "added": 0,
            "duplicates": 0,
            "errors": 0,
        }
        
        for _, row in df.iterrows():
            try:
                result = self.add_reference(
                    title=row["Title"],
                    authors=row.get("Authors", ""),
                    journal=row.get("Journal", ""),
                    year=int(row["Year"]) if row.get("Year") else None,
                    doi=row.get("DOI", ""),
                    link=row.get("Link", ""),
                    category_name=row.get("Category", ""),
                    arxiv_id=row.get("ArxivID", ""),
                )
                
                if result:
                    stats["added"] += 1
                else:
                    stats["duplicates"] += 1
                    
            except Exception as e:
                stats["errors"] += 1
                print(f"Error migrating {row.get('Title', 'Unknown')}: {e}")
        
        return stats

    def export_to_csv(self, csv_file: str) -> int:
        """Export database references to CSV file.
        
        Args:
            csv_file: Path to output CSV file
            
        Returns:
            Number of references exported
        """
        import pandas as pd
        
        session = get_session(self.engine)
        references = session.query(Reference).all()
        session.close()
        
        data = []
        for ref in references:
            data.append({
                "Title": ref.title,
                "Authors": ref.authors or "",
                "Journal": ref.journal or "",
                "Year": ref.year or "",
                "DOI": ref.doi or "",
                "Link": ref.link or "",
                "Category": ref.category.name if ref.category else "",
                "ArxivID": ref.arxiv_id or "",
            })
        
        df = pd.DataFrame(data)
        df = df[["Title", "Authors", "Journal", "Year", "DOI", "Link", "Category", "ArxivID"]]
        df.to_csv(csv_file, index=False)
        
        return len(data)
