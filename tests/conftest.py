import pytest
from httpx import AsyncClient, ASGITransport, Response
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI

from testcontainers.postgres import PostgresContainer

from app.utils.database import Base, get_async_session
from app.main import app
from app.models.city_model import City
from app.utils.open_weather_api import get_open_weather_client


class MockWeatherClient:
    """A mock weather client"""

    async def fetch_weather_data_from_api(self, lat: float, lon: float):
        """Return mock weather data"""
        response_content = b'{"current": {"dt": 1726217388,"sunrise": 1726232901,"sunset": 1726279113,"temp": 8.27,"feels_like": 7.32,"pressure": 1008,"humidity": 95,"dew_point": 7.52,"uvi": 0,"clouds": 99,"visibility": 10000,"wind_speed": 1.84,"wind_deg": 332,"wind_gust": 1.87,"weather": [{"id": 804,"main": "Clouds","description": "overcast clouds","icon": "04n"}]}}'
        return Response(status_code=200, content=response_content)


@pytest.fixture(
    scope="session",
    params=[pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop")],
)
def anyio_backend(request):
    """
    Returns the specified backend ('asyncio' or 'asyncio+uvloop') for testing.
    """
    return request.param


@pytest.fixture(scope="session")
async def test_db():
    """
    Creates and returns a test database URL.
    """
    with PostgresContainer("postgres:14", driver="asyncpg") as postgres:
        test_db_url = postgres.get_connection_url()
        engine = create_async_engine(test_db_url, echo=True)

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            await connection.execute(
                insert(City).values((1, "Calgary", 51.04, -114.06))
            )

        yield test_db_url

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def myapp(test_db) -> FastAPI:
    """
    Creates and returns a FastAPI application instance with overridden dependencies.
    """

    def override_get_db():
        engine = create_async_engine(test_db, echo=True)
        TestSessionLocal = sessionmaker(
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            bind=engine,
            class_=AsyncSession,
        )

        async def _get_db():
            async with TestSessionLocal() as session:
                yield session

        return _get_db

    def mock_weather_client():
        return MockWeatherClient()

    app.dependency_overrides[get_async_session] = override_get_db()
    app.dependency_overrides[get_open_weather_client] = mock_weather_client
    return app


@pytest.fixture(scope="session")
async def client(myapp):
    """
    Creates and returns an HTTPX async client for testing.
    """
    transport = ASGITransport(app=myapp)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
