import sys

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import SQLModel
from sqlmodel import create_engine, Session


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///tasks.sqlite3"
    DEBUG: bool = True
    LOG_LEVEL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def level(self):
        return self.LOG_LEVEL or ("DEBUG" if self.DEBUG else "WARNING")


settings = Settings()

logger.remove()
logger.add(
    sys.stderr,
    level=settings.level,
    colorize=True,
    backtrace=True,
    diagnose=False,
    enqueue=True,
)

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    logger.success("Successfully connected to database")


def get_session():
    with Session(engine) as session:
        yield session
