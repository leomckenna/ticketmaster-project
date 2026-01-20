BEGIN;

CREATE TABLE IF NOT EXISTS venues (
  venue_id   TEXT PRIMARY KEY,
  venue_name TEXT,
  city       TEXT,
  state      TEXT,
  country    TEXT,
  lat        REAL,
  lon        REAL
);

CREATE INDEX IF NOT EXISTS idx_venues_city ON venues (city, state, country);


CREATE TABLE IF NOT EXISTS artists (
  artist_id   TEXT PRIMARY KEY,
  artist_name TEXT
);

CREATE INDEX IF NOT EXISTS idx_artists_name ON artists (artist_name);


CREATE TABLE IF NOT EXISTS events (
  event_id               TEXT PRIMARY KEY,
  name                   TEXT,
  url                    TEXT,
  type                   TEXT,
  locale                 TEXT,
  status                 TEXT,
  datetime               TIMESTAMP,
  onsale_date            TIMESTAMP,
  offsale_date           TIMESTAMP,
  segment                TEXT,
  genre                  TEXT,
  subgenre               TEXT,
  family                 BOOLEAN,
  artist_id              TEXT REFERENCES artists(artist_id) ON UPDATE CASCADE ON DELETE SET NULL,
  venue_id               TEXT REFERENCES venues(venue_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_events_datetime ON events (datetime);
CREATE INDEX IF NOT EXISTS idx_events_venue ON events (venue_id);
CREATE INDEX IF NOT EXISTS idx_events_artist ON events (artist_id);


CREATE TABLE IF NOT EXISTS event_price_history (
  event_id      TEXT NOT NULL REFERENCES events(event_id) ON UPDATE CASCADE ON DELETE CASCADE,
  snapshot_date TIMESTAMP NOT NULL,
  min_price     REAL,
  max_price     REAL,
  currency      TEXT,
  PRIMARY KEY (event_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_price_snapshot ON event_price_history (snapshot_date);


COMMIT;
