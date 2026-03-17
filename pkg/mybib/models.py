"""SQLAlchemy ORM models for bibliography management."""

from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Category(Base):
    """Category model for organizing references."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    references = relationship("Reference", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Reference(Base):
    """Reference model for bibliography entries."""

    __tablename__ = "references"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(String(2000), nullable=True)
    journal = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True, index=True)
    doi = Column(String(255), nullable=True, unique=True, index=True)
    link = Column(String(2000), nullable=True)
    arxiv_id = Column(String(50), nullable=True, index=True)
    scholar_id = Column(String(100), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="references")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_title_year", "title", "year"),
        Index("ix_year_category", "year", "category_id"),
    )

    def __repr__(self):
        return f"<Reference(id={self.id}, title='{self.title[:50]}...', year={self.year})>"


def create_db_engine(db_url: str = "sqlite:///bibliography.db"):
    """Create database engine.
    
    Args:
        db_url: Database URL (default: SQLite)
        
    Returns:
        SQLAlchemy engine
    """
    return create_engine(db_url, echo=False)


def init_db(engine):
    """Initialize database tables.
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def get_session(engine):
    """Get database session.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        SQLAlchemy session
    """
    Session = sessionmaker(bind=engine)
    return Session()
