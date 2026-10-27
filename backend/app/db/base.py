"""SQLAlchemy declarative Base shared across all models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
