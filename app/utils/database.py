from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import settings
from app.utils.exceptions import ServiceError

# Connect to the database and create the tables
engine = create_async_engine(
    settings.DATABASE_URL + settings.DATABASE_NAME, echo=settings.ECHO_SQL
)
asyncSession = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


async def get_async_session():
    """
    Provide a transactional scope around a series of database operations.
    """
    try:
        async with asyncSession.begin() as session:
            yield session
        await session.close()
    except SQLAlchemyError:
        raise ServiceError(message="Failed to establish database connection")


async def init_models() -> None:
    """
    Create the database tables if they do not exist.
    """
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    except SQLAlchemyError:
        raise ServiceError(message="Failed to create database tables")
