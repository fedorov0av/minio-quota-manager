from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.core import engine
from app.db.utils import utcnow
from datetime import datetime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin class that provides automatic timestamp fields for SQLModel classes."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=utcnow(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=utcnow(),
        onupdate=utcnow(),
    )


class DBMixin(DeclarativeBase, TimestampMixin):
    """Base mixin class for SQLModel entities with automatic timestamp tracking."""

    pass


class BucketDB(DBMixin):
    __tablename__ = "bucket"

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_name: Mapped[str] = mapped_column(String(128), unique=True)
    bucket_last_clean: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=utcnow(),
    )


class DirectoryDB(DBMixin):
    __tablename__ = "directory"

    id: Mapped[int] = mapped_column(primary_key=True)
    dir_path: Mapped[str] = mapped_column(String(512), unique=True)
    dir_bucket_id: Mapped[int] = mapped_column(ForeignKey("bucket.id"))
    dir_bucket: Mapped["BucketDB"] = relationship()
    dir_last_clean: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=utcnow(),
    )


if __name__ == "__main__":
    Base.metadata.create_all(engine)
