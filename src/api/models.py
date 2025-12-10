"""
Database Models for User Authentication System

This module defines the User model for storing user credentials securely.
Passwords are hashed using bcrypt before storage.

Reference: #models.py - User data model with secure password handling
"""

from datetime import datetime, timezone
from typing import Optional

import bcrypt
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


# Helper function for datetime defaults
def _utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class User(Base):
    """
    User model for authentication system.

    Stores user credentials with secure password hashing using bcrypt.
    Follows security best practices for password storage.

    Attributes:
        id: Primary key, auto-incrementing integer
        username: Unique username (3-50 characters)
        email: Unique email address
        password_hash: Bcrypt hashed password (never store plain text)
        full_name: Optional full name
        is_active: Account active status (default: True)
        created_at: Account creation timestamp
        updated_at: Last update timestamp

    Reference: #User model - Secure user storage with bcrypt hashing
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now, nullable=False)

    def set_password(self, password: str) -> None:
        """
        Hash and set user password using bcrypt.

        Args:
            password: Plain text password to hash

        Security:
            - Uses bcrypt with automatic salt generation
            - Cost factor of 12 (balanced security/performance)
            - Never stores plain text passwords

        Reference: #set_password - Bcrypt password hashing implementation
        """
        # Generate salt and hash password with cost factor 12
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise

        Reference: #check_password - Password verification using bcrypt
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self) -> dict:
        """
        Convert user object to dictionary (excludes password hash).

        Returns:
            Dictionary with user data (safe for API responses)

        Security:
            - Password hash is NEVER included in output
            - Only safe fields are exposed

        Reference: #to_dict - Safe user serialization without password
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class DatabaseManager:
    """
    Database connection and session management.

    Provides centralized database operations for the authentication system.

    Reference: #DatabaseManager - Database initialization and session management
    """

    def __init__(self, database_url: str = "sqlite:///data/users.db"):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL (default: SQLite in data/ directory)
        """
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self) -> None:
        """
        Create all database tables if they don't exist.

        Safe to call multiple times - only creates missing tables.

        Reference: #create_tables - Database schema initialization
        """
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Get a new database session.

        Returns:
            SQLAlchemy session object

        Usage:
            session = db_manager.get_session()
            try:
                # ... database operations ...
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

        Reference: #get_session - Session factory for database operations
        """
        return self.SessionLocal()

    def drop_tables(self) -> None:
        """
        Drop all database tables (USE WITH CAUTION - DATA LOSS).

        Only use for testing or complete reset scenarios.

        Reference: #drop_tables - Database cleanup (testing only)
        """
        Base.metadata.drop_all(self.engine)
