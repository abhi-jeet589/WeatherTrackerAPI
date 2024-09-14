from fastapi import HTTPException, status


class WeatherTrackerAPIError(HTTPException):
    """Base exception class for Shopping App"""

    def __init__(self, message: str = "Service is unavailable", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.status_code, self.message)


class EntityDoesNotExistError(WeatherTrackerAPIError):
    """Entity does not exist"""

    pass


class ServiceError(WeatherTrackerAPIError):
    """Service is unavailable likely caused by an integrated third party service"""

    pass
