from sqlalchemy.orm import Session
from . import services, models, schemas, database

def fetch_and_store_events(db: Session, lat: float, lng: float, radius_km: int):
    """
    Fetches events from all integrated services and stores them in the database.

    A more production-ready implementation would handle updates to existing events
    and be more robust against duplicates, for example by using a unique
    source-specific ID. For this project, we'll use the event URL as a
    simple unique identifier to prevent duplicate entries.
    """
    print("Starting event fetching and storage task...")

    # Fetch events from all sources
    ticketmaster_events = services.fetch_ticketmaster_events(lat, lng, radius_km)
    eventbrite_events = services.fetch_eventbrite_events(lat, lng, radius_km) # This is a placeholder

    all_events = ticketmaster_events + eventbrite_events

    print(f"Fetched {len(all_events)} events in total.")

    stored_count = 0
    for event_schema in all_events:
        # Check if an event with the same URL already exists
        exists = db.query(models.Event).filter(models.Event.url == str(event_schema.url)).first()

        if not exists:
            db_event = models.Event(**event_schema.dict())
            db.add(db_event)
            stored_count += 1

    db.commit()
    print(f"Stored {stored_count} new events in the database.")


def run_task():
    """
    A wrapper function to be called by a cron job or scheduler.
    This provides a default location to fetch events for.
    In a real application, this might fetch for multiple locations.
    """
    # Using a sample location (e.g., San Francisco) for the task.
    # In a real-world scenario, you might have a list of locations to update.
    DEFAULT_LAT = 37.7749
    DEFAULT_LNG = -122.4194
    DEFAULT_RADIUS_KM = 50

    db = next(database.get_db())
    try:
        # Before fetching, we can clean up old events (e.g., older than 1 day)
        # This is commented out as it might not be desired behavior, but is good practice.
        # from datetime import datetime, timedelta
        # cutoff_date = datetime.utcnow() - timedelta(days=1)
        # db.query(models.Event).filter(models.Event.start_datetime < cutoff_date).delete()
        # db.commit()
        # print("Cleaned up old events.")

        fetch_and_store_events(db, DEFAULT_LAT, DEFAULT_LNG, DEFAULT_RADIUS_KM)
    finally:
        db.close()


if __name__ == "__main__":
    # This allows running the task manually for testing.
    # Make sure to set up your .env file with the necessary API keys.
    print("Running event fetching task manually...")
    # We need to create the database tables first if they don't exist
    from .database import engine
    from .models import Base
    print("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    run_task()
    print("Task finished.")
