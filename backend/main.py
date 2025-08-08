from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
from math import radians, sin, cos, sqrt, atan2

from . import models, schemas, database

# Create all database tables on startup
# In a production app, you might use Alembic for migrations.
models.Base.metadata.create_all(bind=database.engine)


app = FastAPI(
    title="Tonight In-Town API",
    description="API for finding events happening near you in the next 12 hours.",
    version="0.1.0",
)


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth in kilometers.
    """
    R = 6371  # Radius of Earth in kilometers

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/events/", response_model=List[schemas.Event])
def get_events(
    lat: float,
    lng: float,
    radius_km: int = 10,
    db: Session = Depends(database.get_db),
):
    """
    Get events near a specific location.

    - **lat**: Latitude of the user's location.
    - **lng**: Longitude of the user's location.
    - **radius_km**: Search radius in kilometers.
    """
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(status_code=400, detail="Invalid latitude or longitude.")

    now = datetime.now(timezone.utc)
    twelve_hours_later = now + timedelta(hours=12)

    # Query events that are starting in the next 12 hours.
    # Note: For a very large database, filtering by distance should be done in the DB query
    # itself, ideally using a spatial index (e.g., with PostGIS).
    # For this project, we fetch a broader set of recent events and filter in Python.
    potential_events = (
        db.query(models.Event)
        .filter(models.Event.start_datetime.between(now, twelve_hours_later))
        .order_by(models.Event.start_datetime.asc())
        .limit(500) # Limit the number of events to process
        .all()
    )

    nearby_events = []
    for event in potential_events:
        event_lat = float(event.lat)
        event_lng = float(event.lng)

        distance = haversine(lat, lng, event_lat, event_lng)

        if distance <= radius_km:
            nearby_events.append(event)

    return nearby_events
