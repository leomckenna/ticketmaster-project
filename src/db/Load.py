"""
Load normalized data files (CSV) and populate the SQLite tables
"""

import argparse, sqlite3, pandas as pd
from pathlib import Path
# from ..config import TRANSFORMED_DIR # TODO: fix module import

ap = argparse.ArgumentParser()
ap.add_argument("--db", required=True)
ap.add_argument("--indir", default="data/transformed_data") # TODO: fix module import
args = ap.parse_args()

# input directory for data and the schema
indir = Path(args.indir)
schema_path = Path(__file__).resolve().parent / "schema.sql"

def load_csv(name): 
    """Load CSV files"""
    p = indir / f"{name}.csv"
    if not p.exists(): 
        raise SystemExit(f"missing input: {p}")
    return pd.read_csv(p)

# load CSV files for tables
venues = load_csv("venues")
artists = load_csv("artists")
events = load_csv("events")
eph = load_csv("event_price_history")

# connect to SQLite and create schema
conn = sqlite3.connect(args.db) # creates DB at root if it doesn't exist
conn.executescript(schema_path.read_text(encoding="utf-8"))
cur = conn.cursor()

# upsert into tables
cur.executemany("""
INSERT INTO venues (venue_id, venue_name, city, state, country, lat, lon)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(venue_id) DO UPDATE SET
  venue_name=excluded.venue_name, city=excluded.city, state=excluded.state,
  country=excluded.country, lat=excluded.lat, lon=excluded.lon;
""", venues.where(pd.notna(venues), None).to_records(index=False)) # convert NaN to None for SQLite

cur.executemany("""
INSERT INTO artists (artist_id, artist_name)
VALUES (?, ?)
ON CONFLICT(artist_id) DO UPDATE SET artist_name=excluded.artist_name;
""", artists.where(pd.notna(artists), None).to_records(index=False))

cur.executemany("""
INSERT INTO events (
  event_id, name, url, type, locale, datetime, status, onsale_date, offsale_date,
  segment, genre, subgenre, family, artist_id, venue_id
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(event_id) DO UPDATE SET
  name=excluded.name, url=excluded.url, type=excluded.type, locale=excluded.locale,
  datetime=excluded.datetime, status=excluded.status,
  onsale_date=excluded.onsale_date, offsale_date=excluded.offsale_date,
  segment=excluded.segment, genre=excluded.genre, subgenre=excluded.subgenre,
  family=excluded.family, artist_id=excluded.artist_id, venue_id=excluded.venue_id;
""", events.where(pd.notna(events), None).to_records(index=False))

cur.executemany("""
INSERT INTO event_price_history (event_id, snapshot_date, min_price, max_price, currency)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT(event_id, snapshot_date) DO UPDATE SET
  min_price=excluded.min_price, max_price=excluded.max_price, currency=excluded.currency;
""", eph.where(pd.notna(eph), None).to_records(index=False))

# close connection
conn.commit()
conn.close()
print("Loaded tables to", args.db)
