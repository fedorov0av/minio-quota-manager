from pydantic_settings import BaseSettings
from pydantic_core import MultiHostUrl
from pydantic import computed_field


class Config(BaseSettings):
    MINIO_URL: str = "localhost"

    MINIO_ACCESS_KEY: str = "ACCESS_KEY"
    MINIO_SECRET_KEY: str = "SECRET_KEY"
    MINIO_API_PORT: int = 9000
    PERCENT_DELETE_FILES: int = 10
    CERT_CHECK: bool = False
    SECURE: bool = False
    CLEAN_PERCENT: int = 10

    POSTGRES_SERVER: str = "msc-db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changethis"
    POSTGRES_DB: str = "msc"

    REDIS_URL: str = "localhost"
    REDIS_PORT: int = 6379

    TASK_DIR_TIME_MINUTES: int = 30
    TASK_CLEAN_TIME_MINUTES: int = 10

    LOG_FILE: str = "logs/celery.log"

    class Config:
        env_file = ".env"
        extra = "allow"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:
        """Construct and return the SQLAlchemy database URI."""
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Config()
