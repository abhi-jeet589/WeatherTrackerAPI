from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.utils.database import get_async_session
from app.services.weather_service import WeatherService
from app.schemas.weather_history_schema import WeatherHistoryResponse
from app.schemas.weather_response_schema import WeatherResponseSchema
from app.utils.open_weather_api import get_open_weather_client

router = APIRouter(prefix="/weather", tags=["Weather"])

limiter = Limiter(key_func=get_remote_address)


@router.get("/history")
async def get_weather_history(
    session: AsyncSession = Depends(get_async_session),
) -> List[WeatherHistoryResponse]:
    """
    Fetch all successful weather requests from the database.
    """
    weather_service = WeatherService(session)
    return await weather_service.get_weather_history()


@router.get("/{city_id}")
@limiter.limit("1/second")  # 1 per second to make sure not to overwhelm the server
@limiter.limit("30/hour")  # Half the limit provided by OpenWeatherMap API service
async def get_weather(
    request: Request,
    city_id: int,
    session: AsyncSession = Depends(get_async_session),
    open_weather_api_client=Depends(get_open_weather_client),
) -> WeatherResponseSchema:
    """
    Fetch the weather data for the provided city ID from the OpenWeatherMap API.
    """
    weather_service = WeatherService(session)
    return await weather_service.get_weather_data(city_id, open_weather_api_client)
