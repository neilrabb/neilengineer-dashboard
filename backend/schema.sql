-- This schema is for PostgreSQL and requires the PostGIS extension for efficient location-based querying.
-- To enable PostGIS, run: CREATE EXTENSION postgis;

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_datetime TIMESTAMPTZ NOT NULL,
    end_datetime TIMESTAMPTZ,
    venue_name VARCHAR(255),
    lat DECIMAL(9, 6) NOT NULL,
    lng DECIMAL(9, 6) NOT NULL,
    price_min DECIMAL(10, 2),
    url VARCHAR(2048) NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Optional: Create a spatial index for faster location-based queries if using PostGIS.
-- This allows for using functions like ST_DWithin for radius searches.
-- CREATE INDEX idx_events_location ON events USING gist (ST_MakePoint(lng, lat));

-- A simpler index for non-PostGIS setups, though less efficient for radius searches.
CREATE INDEX idx_events_start_datetime ON events (start_datetime);
