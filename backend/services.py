import os
import requests
import pygeohash as pgh
from datetime import datetime, timedelta, timezone

from . import models, schemas
from .database import SessionLocal


TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
TICKETMASTER_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
EVENTBRITE_API_URL = "https://www.eventbriteapi.com/v3/events/search/"


def fetch_ticketmaster_events(lat: float, lng: float, radius_km: int):
    """
    Fetches events from the Ticketmaster Discovery API.
    """
    if not TICKETMASTER_API_KEY:
        print("Warning: TICKETMASTER_API_KEY is not set. Skipping Ticketmaster API call.")
        return []

    # Get the current time and the time 12 hours from now in ISO 8601 format
    start_datetime = datetime.now(timezone.utc)
    end_datetime = start_datetime + timedelta(hours=12)

    # Convert to the format required by the Ticketmaster API (YYYY-MM-DDTHH:mm:ssZ)
    start_datetime_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_datetime_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Generate geohash for the location
    geohash = pgh.encode(lat, lng, precision=5)

    params = {
        "apikey": TICKETMASTER_API_KEY,
        "geoPoint": geohash,
        "radius": radius_km,
        "unit": "km",
        "startDateTime": start_datetime_str,
        "endDateTime": end_datetime_str,
        "sort": "date,asc",
        "size": 100,  # Max 1000, but 100 is a reasonable limit for this app
    }

    try:
        response = requests.get(TICKETMASTER_API_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if "_embedded" not in data:
            return []

        events = []
        for event_data in data.get("_embedded", {}).get("events", []):
            try:
                venue = event_data.get("_embedded", {}).get("venues", [{}])[0]
                price_range = event_data.get("priceRanges", [{}])[0]

                event = schemas.EventCreate(
                    name=event_data.get("name"),
                    start_datetime=event_data.get("dates", {}).get("start", {}).get("dateTime"),
                    end_datetime=event_data.get("dates", {}).get("end", {}).get("dateTime"),
                    venue_name=venue.get("name"),
                    lat=venue.get("location", {}).get("latitude"),
                    lng=venue.get("location", {}).get("longitude"),
                    price_min=price_range.get("min"),
                    url=event_data.get("url"),
                    source="ticketmaster",
                )
                events.append(event)
            except (KeyError, IndexError, TypeError) as e:
                print(f"Skipping a Ticketmaster event due to parsing error: {e}")
                continue
        return events
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Ticketmaster: {e}")
        return []


def fetch_eventbrite_events(lat: float, lng: float, radius_km: int):
    """
    Placeholder for fetching events from the Eventbrite API.
    This is not implemented due to issues accessing the API documentation.
    """
    print("Warning: Eventbrite API integration is not implemented.")
    if not EVENTBRITE_API_KEY:
        print("Warning: EVENTBRITE_API_KEY is not set.")

    # To simulate a successful call with no events
    return []
