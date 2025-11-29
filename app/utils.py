import os
from pathlib import Path
from typing import Union
from loguru import logger

from collections.abc import Generator
from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.core import engine


@contextmanager
def get_session() -> Generator[Session]:
    """Get DB session."""
    with Session(engine) as session:
        yield session


def file_exists(
    file_path: Union[str, Path], content: str = "", encoding: str = "utf-8"
) -> bool:
    try:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                return True
            else:
                return False
        path.parent.mkdir(mode=777, parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        logger.info(f"File created: {file_path}")
        os.chmod(file_path, 0o777)
        return True
    except Exception as e:
        logger.error(f"Error from create file: {e}")
        return False
