from pydantic import BaseModel


class DirModel(BaseModel):
    path: str | None
    check: bool
    finish_dir: bool
    bucket_name: str
