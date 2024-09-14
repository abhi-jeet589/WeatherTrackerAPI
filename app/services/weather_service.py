from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import TimeoutException, HTTPStatusError

from app.config.settings import settings
from app.models.city_model import City
from app.models.weather_logger_model import WeatherLogger
from app.schemas.weather_history_schema import WeatherHistoryResponse
from app.utils.exceptions import EntityDoesNotExistError, ServiceError
from app.schemas.weather_response_schema import WeatherResponseSchema

WEATHER_LOG_SUCCESS_VAL = "Success"
WEATHER_LOG_FAILURE_VAL = "Failure"


class WeatherService:
    def __init__(self, session: AsyncSession):
        """
        Initialize the weather service with the provided SQLAlchemy session.

        :param session: The SQLAlchemy session to use for database operations.
        """
        self.api_key = settings.API_KEY
        self.base_url = settings.API_BASE_URL
        self.session = session

    async def _fetch_city_details(self, city_id: int):
        """
        Fetch the city details from the database based on the provided city ID.

        :param city_id: The ID of the city to fetch.
        :return: The city details if found, otherwise raises an EntityDoesNotExistError.
        """
        city = await self.session.execute(select(City).where(City.id == city_id))
        city_in_db = city.scalar()
        if not city_in_db:
            raise EntityDoesNotExistError(message="City not found", status_code=404)
        return city_in_db

    async def log_weather_request(
        self,
        city_id: int,
        response_code: int,
        response_status: str,
        summary: str = "",
    ):
        """
        Log the weather request details to the database.

        :param city_id: The ID of the city.
        :param response_code: The HTTP response status code.
        :param response_status: The HTTP response status.
        :param summary: (optional) Additional information about the weather request.
        """
        weather_log = WeatherLogger(
            city_id=city_id,
            response_code=response_code,
            response_status=response_status,
            response=summary,
        )
        self.session.add(weather_log)
        await self.session.commit()

    async def get_weather_data(self, city_id: int, api_client) -> WeatherResponseSchema:
        """
        Fetch the weather data for the provided city ID from the OpenWeatherMap API and log the request details.

        :param city_id: The ID of the city.
        :param api_client: The OpenWeatherMap API client to use.
        """
        city = await self._fetch_city_details(city_id)

        try:
            response = await api_client.fetch_weather_data_from_api(
                city.latitude, city.longitude
            )
            current_weather = response.json()["current"]
            await self.log_weather_request(
                city_id,
                response.status_code,
                WEATHER_LOG_SUCCESS_VAL,
                summary=current_weather["weather"][0]["main"],
            )  # Log the request status code
            return WeatherResponseSchema(
                id=city.id,
                city_name=city.name,
                current_weather=current_weather,
            )
        except HTTPStatusError:
            await self.log_weather_request(
                city_id, 500, WEATHER_LOG_FAILURE_VAL
            )  # Log the request status code
            raise ServiceError(
                message=f"Failed to fetch weather data",
                status_code=500,
            )
        except TimeoutException:
            await self.log_weather_request(
                city_id, 504, WEATHER_LOG_FAILURE_VAL
            )  # Log the request status code
            raise ServiceError(message="Timeout fetching weather data", status_code=504)

    async def get_weather_logs(self) -> list:
        """
        Fetch the last 5 successful weather requests from the database.

        :return: A list of WeatherHistoryResponse objects containing the details of the weather requests.
        """
        results = await self.session.execute(
            select(
                City.name,
                WeatherLogger.response,
                WeatherLogger.response_code,
                WeatherLogger.response_status,
                WeatherLogger.created_at,
            )
            .join(City, WeatherLogger.city_id == City.id)
            .where(WeatherLogger.response_status == "Success")
            .order_by(WeatherLogger.created_at.desc())
            .limit(5)
        )
        return results.fetchall()

    async def get_weather_history(self) -> list:
        """
        Fetch all successful weather requests from the database and return them in a list of WeatherHistoryResponse objects.

        :return: A list of WeatherHistoryResponse objects containing the details of the weather requests.
        """
        results = await self.get_weather_logs()
        return [
            WeatherHistoryResponse(
                created_at=row.created_at,
                response_code=row.response_code,
                response_status=row.response_status,
                name=row.name,
                summary=row.response,
            )
            for row in results
        ]
