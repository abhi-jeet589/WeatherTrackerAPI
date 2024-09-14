from httpx import AsyncClient, TimeoutException, HTTPStatusError

from app.config.settings import settings


class OpenWeatherAPIClient:
    """
    A client for making requests to the OpenWeatherMap API.
    """

    def __init__(self):
        """
        Initialize the OpenWeatherMap API client with the provided API key and base URL.
        """
        self.base_url = settings.API_BASE_URL
        self.api_key = settings.API_KEY

    async def fetch_weather_data_from_api(self, lat: float, lon: float):
        """
        Fetch the weather data for the given latitude and longitude from the OpenWeatherMap API.

        :param lat: The latitude of the location.
        :param lon: The longitude of the location.
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "exclude": "minutely,hourly,daily,alerts",
        }

        async with AsyncClient() as client:
            try:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                return response
            except HTTPStatusError:
                raise
            except TimeoutException:
                raise


def get_open_weather_client() -> OpenWeatherAPIClient:
    """
    Factory function to create and return an instance of the OpenWeatherAPIClient.
    """
    return OpenWeatherAPIClient()
