import datetime
from pydantic import BaseModel, AnyHttpUrl
from decimal import Decimal


class EventBase(BaseModel):
    name: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime | None = None
    venue_name: str | None = None
    lat: Decimal
    lng: Decimal
    price_min: Decimal | None = None
    url: AnyHttpUrl
    source: str


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
