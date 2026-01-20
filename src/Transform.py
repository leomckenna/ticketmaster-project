"""
Normalize a flat events dataset into SQLite tables:
- venues(venue_id, venue_name, city, state, country, lat, lon)
- artists(artist_id, artist_name)
- events(event_id, name, url, type, locale, datetime, status, onsale_date, offsale_date,
        segment, genre, subgenre, family, artist_id, venue_id)
- event_price_history(event_id, snapshot_date, min_price, max_price, currency)
"""

import argparse
import pandas as pd
from config import TRANSFORMED_DIR 
from pathlib import Path

def to_ts(x): 
    """Convert to timestamp"""
    return pd.to_datetime(x, errors="coerce")

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--outdir", default=TRANSFORMED_DIR)
args = ap.parse_args()

# create output directory
outdir = Path(args.outdir)
outdir.mkdir(parents=True, exist_ok=True)

# read raw data file
df = pd.read_parquet(args.data, engine="fastparquet")

# venues
venues = (
    df[["venue_id","venue","city","state","country","venue_lat","venue_lon"]]
    .dropna(subset=["venue_id"])
    .drop_duplicates("venue_id")
    .rename(columns={
        "venue":"venue_name",
        "venue_lat":"lat",
        "venue_lon":"lon"
    })
)[["venue_id","venue_name","city","state","country","lat","lon"]]

# artists
artists = (
    df[["artist_id","artist"]]
    .dropna(subset=["artist_id"])
    .drop_duplicates("artist_id")
    .rename(columns={"artist":"artist_name"})
)[["artist_id","artist_name"]]

# events
# build datetime column from date + optional time
date_str = df["date"].astype(str)
time_str = df.get("time", "").fillna("").astype(str)

datetime_col = pd.to_datetime(
    date_str + " " + time_str,
    errors="coerce"
).fillna(pd.to_datetime(df["date"], errors="coerce"))

events = pd.DataFrame({
    "event_id": df["id"],
    "name": df.get("name"),
    "url": df.get("url"),
    "type": df.get("type"),
    "locale": df.get("locale"),
    "datetime": datetime_col,
    "status": df.get("status"),
    "onsale_date": to_ts(df.get("onsale_date")),
    "offsale_date": to_ts(df.get("offsale_date")),
    "segment": df.get("segment"),
    "genre": df.get("genre"),
    "subgenre": df.get("subgenre"),
    "family": df.get("family"),
    "artist_id": df.get("artist_id"),
    "venue_id": df.get("venue_id"),
})
events["family"] = events["family"].map({"TRUE": 1, "FALSE": 0}) # normalize boolean to 0/1
events = events.dropna(subset=["event_id"]).drop_duplicates("event_id")

# event_price_history
eph = pd.DataFrame({
    "event_id": df["id"],
    "snapshot_date": to_ts(df.get("snapshot_date")),
    "min_price": pd.to_numeric(df.get("min_price"), errors="coerce"),
    "max_price": pd.to_numeric(df.get("max_price"), errors="coerce"),
    "currency": df.get("currency"),
})
eph = eph.dropna(subset=["event_id","snapshot_date"]).drop_duplicates(["event_id","snapshot_date"])

# write CSVs
venues.to_csv(outdir/"venues.csv", index=False)
artists.to_csv(outdir/"artists.csv", index=False)
events.to_csv(outdir/"events.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
eph.to_csv(outdir/"event_price_history.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
print(f"Wrote transformed data files (CSV) to '{outdir}'")
