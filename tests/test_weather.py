import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_weather_data(client: AsyncClient):
    """
    Test the GET /weather/{city_id} endpoint.
    """
    response = await client.get(url="/weather/1")
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["city_name"] == "Calgary"
    assert "current_weather" in response_data


@pytest.mark.anyio
async def test_get_historical_weather_data(client: AsyncClient):
    """
    Test the GET /weather/history endpoint.
    """
    response = await client.get(url="/weather/history")
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) >= 0
    if len(response_data) > 0:
        assert "created_at" in response_data[0]
        assert "response_code" in response_data[0]
        assert "response_status" in response_data[0]
        assert "name" in response_data[0]
        assert "summary" in response_data[0]
