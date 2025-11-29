import json
from datetime import datetime
from app.core import admin_client, minio_client
from app.schemas.models import DirModel
from app.db.crud import (
    get_directoryDB_sort_last_clean,
    get_bucket,
    update_bucket_last_clean,
    update_directory_last_clean,
)
from app.config import settings
from loguru import logger


def get_objects_sorted_by_date(bucket_name: str, prefix: str | None = None):
    """Get objects sorted by date."""

    objects = minio_client.list_objects(bucket_name, prefix=prefix, recursive=True)
    objects_list = list(objects)
    objects_list.sort(key=lambda x: x.last_modified)
    return objects_list


def get_bucket_size(bucket_name: str) -> int | None:
    try:
        sizes_res: dict = json.loads(admin_client.get_data_usage_info())
    except json.decoder.JSONDecodeError:
        return None
    bct_sizes_res: dict | None = sizes_res.get("bucketsSizes")
    if bct_sizes_res is None:
        return None
    return bct_sizes_res.get(bucket_name)


def get_bucket_count_object(bucket_name: str) -> int:
    sizes_res: dict = json.loads(admin_client.get_data_usage_info())
    bcts_usage_info: dict = sizes_res.get("bucketsUsageInfo")
    bct_usage_info: dict = bcts_usage_info.get(bucket_name)
    return bct_usage_info.get("objectsCount")


def get_last_update_info() -> datetime:
    sizes_res: dict = json.loads(admin_client.get_data_usage_info())
    last_update_info: str = sizes_res.get("lastUpdate")
    return datetime.fromisoformat(last_update_info.replace("Z", "+00:00"))


def get_bucket_quota_size(bucket_name: str) -> int | None:
    try:
        quota_res: dict = json.loads(admin_client.bucket_quota_get(bucket=bucket_name))
    except json.decoder.JSONDecodeError:
        return None
    quota_size: int = quota_res.get("quota")
    return quota_size if quota_size != 0 else None


def get_bucket_names_with_quota() -> list[str]:
    return [
        bucket.name
        for bucket in minio_client.list_buckets()
        if get_bucket_quota_size(bucket.name)
    ]


def check_minio_dir(
    dirs_storage: list[DirModel],
    directory: DirModel | None = None,
    bucket_name: str | None = None,
    recursive: bool = False,
):
    if bucket_name is None:
        return
    objects = minio_client.list_objects(
        bucket_name=bucket_name,
        prefix=directory.path if directory is not None else None,
    )
    try:
        for obj in objects:
            if obj.is_dir:
                d = DirModel(
                    path=obj.object_name,
                    check=False,
                    finish_dir=False,
                    bucket_name=bucket_name,
                )
                dirs_storage.append(d)
                if recursive is True:
                    check_minio_dir(dirs_storage, d, bucket_name, recursive)
            else:
                if directory is not None:
                    directory.finish_dir = True
                return
    except ValueError as err:
        logger.error(err)


def check_buck_quota_limit(bucket_name: str) -> bool:
    bc_quota_size = get_bucket_quota_size(bucket_name)
    if bc_quota_size is None:
        return False
    bc_size = get_bucket_size(bucket_name)
    if bc_size is None:
        return False
    percents = round(100 - (bc_size / (bc_quota_size / 100)), 2)
    return True if percents < settings.CLEAN_PERCENT else False


def clean_bucket(bucket_name: str):
    dirs_db = get_directoryDB_sort_last_clean(bucket_name)
    bucket_db = get_bucket(bucket_name)
    if bucket_db is None:
        logger.error(f"Bucket not found! Bucket name: {bucket_name}")
        return
    last_stats_update: datetime = get_last_update_info()
    bucket_last_clean_local_tz = bucket_db.bucket_last_clean.astimezone()
    last_update_stats_local_tz = last_stats_update.astimezone()
    if bucket_last_clean_local_tz > last_update_stats_local_tz:
        logger.info(
            f"Bucket is clean up for last stats update! Bucket last clean : {bucket_last_clean_local_tz}, Last stats update: {last_update_stats_local_tz}"
        )
        return
    if dirs_db is None:
        logger.info(f"Directories is not found! Bucket name: {bucket_name}")
        return
    clean_object_counter = 0

    count_clean_objects_bct = int(
        get_bucket_count_object(bucket_name) / 100 * settings.PERCENT_DELETE_FILES
    )
    for dir_db in dirs_db:
        objs = get_objects_sorted_by_date(bucket_name, prefix=dir_db.dir_path)
        for obj in objs:
            if obj.object_name is None:
                return
            minio_client.remove_object(obj.bucket_name, obj.object_name)
            clean_object_counter += 1
            if clean_object_counter == count_clean_objects_bct:
                logger.info(
                    f"Cleanup completed for bucket: {bucket_name}, Count clean objects: {count_clean_objects_bct}"
                )
                update_bucket_last_clean(bucket_name)
                update_directory_last_clean(dir_db.dir_path)
                return
