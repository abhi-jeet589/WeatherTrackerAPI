from datetime import datetime
from pydantic import BaseModel, Field


class WeatherHistoryResponse(BaseModel):
    """
    Represents a weather history response.
    """

    created_at: datetime = Field(description="Time when the request was made")
    summary: str = Field(description="Summary of the request")
    response_code: int = Field(description="Response code for the request")
    response_status: str = Field(description="Response status for the request")
    name: str = Field(description="Name of the city")
