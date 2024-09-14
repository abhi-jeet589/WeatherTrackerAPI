from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, TIMESTAMP
from sqlalchemy import String, ForeignKey
import datetime

from app.utils.database import Base


class WeatherLogger(Base):
    """
    Represents the weather_loggers table in the database.
    """

    __tablename__ = "weather_loggers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("cities.id"))
    response_code: Mapped[int] = mapped_column(INTEGER)
    response_status: Mapped[str] = mapped_column(String(20))
    response: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.now
    )
