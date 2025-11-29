from sqlalchemy import create_engine
from minio import Minio, MinioAdmin

try:
    from app.config import settings
except ModuleNotFoundError:
    from config import settings

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI), pool_size=20, max_overflow=10
)

minio_client = Minio(
    endpoint=settings.MINIO_URL + ":" + str(settings.MINIO_API_PORT),
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    cert_check=settings.CERT_CHECK,
    secure=settings.SECURE,
)

admin_client = MinioAdmin(
    credentials=minio_client._provider,
    endpoint=minio_client._base_url.host,
    cert_check=settings.CERT_CHECK,
    secure=settings.SECURE,
)
