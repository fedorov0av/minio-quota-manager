from datetime import datetime, timezone
from sqlalchemy.exc import OperationalError, ResourceClosedError
from sqlalchemy import select
from app.db.models import BucketDB, DirectoryDB
from app.utils import get_session
from loguru import logger
from typing import Sequence


def add_bucket(bucket_name: str) -> BucketDB | None:
    """Adds a new bucket to the database."""

    bucket_db = get_bucket(bucket_name)
    if bucket_db is not None:
        return None
    bucket_db = BucketDB(bucket_name=bucket_name)
    with get_session() as session:
        try:
            session.add(bucket_db)
            session.commit()
        except (OperationalError, ResourceClosedError) as e:
            logger.error(
                f"Database write operation failed. Check connection or constraints. Error: {e}"
            )
            session.rollback()
            return None
        else:
            return bucket_db


def get_bucket(bucket_name: str) -> BucketDB | None:
    """Retrieves a bucket from the database by name."""

    with get_session() as session:
        query = select(BucketDB).where(BucketDB.bucket_name == bucket_name)
        return session.scalars(query).one_or_none()


def update_bucket_last_clean(bucket_name: str) -> BucketDB | None:
    """Updates the last clean timestamp for a bucket."""

    bucket_db = get_bucket(bucket_name)
    if bucket_db is None:
        return None
    bucket_db.bucket_last_clean = datetime.now(timezone.utc)
    with get_session() as session:
        try:
            session.add(bucket_db)
            session.commit()
        except (OperationalError, ResourceClosedError) as e:
            logger.error(
                f"Database write operation failed. Check connection or constraints. Error: {e}"
            )
            session.rollback()
            return None
        else:
            return bucket_db


def update_directory_last_clean(dir_path: str) -> DirectoryDB | None:
    """Updates the last clean timestamp for a directory."""

    directory_db = get_directory(dir_path)
    if directory_db is None:
        return None
    directory_db.dir_last_clean = datetime.now(timezone.utc)
    with get_session() as session:
        try:
            session.add(directory_db)
            session.commit()
        except (OperationalError, ResourceClosedError) as e:
            logger.error(
                f"Database write operation failed. Check connection or constraints. Error: {e}"
            )
            session.rollback()
            return None
        else:
            return directory_db


def get_directory(dir_path: str) -> DirectoryDB | None:
    """Retrieves a directory from the database by path."""

    with get_session() as session:
        query = select(DirectoryDB).where(DirectoryDB.dir_path == dir_path)
        return session.scalars(query).one_or_none()


def get_directoryDB_sort_last_clean(bucket_name: str) -> Sequence[DirectoryDB] | None:
    """Retrieves all directories for a bucket sorted by last clean timestamp."""

    directory_db = get_bucket(bucket_name)
    if directory_db is None:
        return None
    with get_session() as session:
        query = (
            select(DirectoryDB)
            .where(DirectoryDB.dir_bucket_id == directory_db.id)
            .order_by(DirectoryDB.dir_last_clean)
        )
        return session.scalars(query).all()


def add_directory(dir_path: str, bucket_name: str) -> DirectoryDB | None:
    """Adds a new directory to the database associated with a bucket."""

    bucket_db = get_bucket(bucket_name)
    if bucket_db is None:
        return None
    if get_directory(dir_path) is not None:
        return None
    directory_db = DirectoryDB(dir_path=dir_path, dir_bucket_id=bucket_db.id)
    with get_session() as session:
        try:
            session.add(directory_db)
            session.commit()
        except (OperationalError, ResourceClosedError) as e:
            logger.error(
                f"Database write operation failed. Check connection or constraints. Error: {e}"
            )
            session.rollback()
        else:
            return directory_db
