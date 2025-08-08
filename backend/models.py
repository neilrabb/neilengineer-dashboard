import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Numeric,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=True)
    venue_name = Column(String(255), nullable=True)
    lat = Column(Numeric(9, 6), nullable=False)
    lng = Column(Numeric(9, 6), nullable=False)
    price_min = Column(Numeric(10, 2), nullable=True)
    url = Column(String(2048), nullable=False)
    source = Column(String(50), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f"<Event(name='{self.name}', start_datetime='{self.start_datetime}')>"
