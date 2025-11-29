from celery import Celery

from app.config import settings
from app.utils import file_exists
from app.minio_utils import (
    check_minio_dir,
    get_bucket_names_with_quota,
    clean_bucket,
    check_buck_quota_limit,
)
from loguru import logger
from app.schemas.models import DirModel
from app.db.crud import add_bucket, add_directory


app = Celery(__name__)
app.config_from_object(__name__)  # type: ignore
app.conf.broker_url = f"redis://{settings.REDIS_URL}:{settings.REDIS_PORT}/0"  # type: ignore
app.conf.beat_schedule = {  # type: ignore
    "check_dirs": {
        "task": f"{__name__}.task_check_dirs",
        "schedule": (settings.TASK_DIR_TIME_MINUTES * 60.0),
        # "schedule": 5.0,
    },
    "clean_bucket": {
        "task": f"{__name__}.task_clean_buckets",
        "schedule": (settings.TASK_CLEAN_TIME_MINUTES * 60.0),
        # "schedule": 5.0,
    },
}
app.conf.timezone = "Europe/Moscow"  # type: ignore


if file_exists(settings.LOG_FILE):
    logger.add(settings.LOG_FILE)


def check_dirs():
    dirs: list[DirModel] = list()
    bucket_names = get_bucket_names_with_quota()
    for bucket_name in bucket_names:
        bucket_db = add_bucket(bucket_name)
        if bucket_db is not None:
            logger.info(f"Bucket added to database! Bucket name: {bucket_name}")
        check_minio_dir(dirs_storage=dirs, bucket_name=bucket_name, recursive=True)
    for dir in dirs:
        if dir.finish_dir is True:
            if dir.path is not None:
                directory_db = add_directory(dir.path, dir.bucket_name)
                if directory_db is not None:
                    logger.info(
                        f"Directory added to database! Bucket name: {dir.bucket_name}, Dir path: {dir.path}"
                    )


def check_buckets():
    bucket_names = get_bucket_names_with_quota()
    for bucket_name in bucket_names:
        if check_buck_quota_limit(bucket_name):
            logger.info(f"Starting bucket cleanup...! Bucket name: {bucket_name}")
            clean_bucket(bucket_name)


check_dirs()


@app.task  # type: ignore
def task_check_dirs():
    check_dirs()


@app.task  # type: ignore
def task_clean_buckets():
    check_buckets()
