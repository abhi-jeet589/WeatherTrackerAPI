from typing import Callable
from fastapi import FastAPI, Request, status
from contextlib import asynccontextmanager
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.routers.weather_router import router as weather_router
from app.utils.database import init_models
from app.utils.exceptions import (
    EntityDoesNotExistError,
    ServiceError,
    WeatherTrackerAPIError,
)
from app.routers.weather_router import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    A context manager for managing the lifespan of the FastAPI application.
    """
    # await init_models()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(weather_router)
app.state.limiter = limiter


def create_exception_handler(
    status_code: int, err_message: str
) -> Callable[[Request, WeatherTrackerAPIError], ORJSONResponse]:
    """
    Create a custom exception handler for the given status code and error message.

    :param status_code: The HTTP status code to return in the response.
    :param err_message: The error message to include in the response.
    """
    detail = {"message": err_message}

    async def exception_handler(
        _: Request, exception: WeatherTrackerAPIError
    ) -> ORJSONResponse:
        if exception.message:
            detail["message"] = exception.message

        return ORJSONResponse(
            status_code=status_code, content={"error": detail["message"]}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=EntityDoesNotExistError,
    handler=create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        err_message="Entity does not exist",
    ),
)
app.add_exception_handler(
    exc_class_or_status_code=ServiceError,
    handler=create_exception_handler(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        err_message="Internal server error occured",
    ),
)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
