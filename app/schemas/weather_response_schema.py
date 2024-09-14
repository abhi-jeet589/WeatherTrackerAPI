from pydantic import BaseModel, Field


class WeatherResponseSchema(BaseModel):
    """
    Represents the weather response schema.
    """

    id: int = Field(description="Id of the city")
    city_name: str = Field(description="Name of the city")
    current_weather: dict = Field(description="Current weather in the city")
