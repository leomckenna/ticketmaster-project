"""
Daily Ticketmaster snapshotter:
- Pulls all 'Music' events for the next 90 days (month-by-month windows)
- Appends to data/events_history.parquet with a snapshot_date
- De-dupes by (id, snapshot_date) so you retain a daily history
"""

import os
import time
from datetime import datetime, timedelta
import requests
import pandas as pd

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
API_KEY = os.getenv("TICKETMASTER_API_KEY")  # set in env / GitHub Secret
OUT_DIR = "data"
OUT_FILE = os.path.join(OUT_DIR, "events_history.parquet")

# --------- helpers ---------
def iso_utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def month_windows(start_dt: datetime, end_dt: datetime):
    cur = datetime(start_dt.year, start_dt.month, 1)
    while cur < end_dt:
        if cur.month == 12:
            nxt = datetime(cur.year + 1, 1, 1)
        else:
            nxt = datetime(cur.year, cur.month + 1, 1)
        yield cur, min(nxt, end_dt)
        cur = nxt

def fetch_page(page=0, size=200, **params):
    if not API_KEY:
        raise RuntimeError("TICKETMASTER_API_KEY is not set.")
    p = {"apikey": API_KEY, "page": page, "size": min(size, 200)}
    p.update({k: v for k, v in params.items() if v is not None})
    r = requests.get(BASE_URL, params=p, timeout=30)
    r.raise_for_status()
    return r.json()

def parse_events_data(data: dict) -> pd.DataFrame:
    if "_embedded" not in data or "events" not in data["_embedded"]:
        return pd.DataFrame()
    rows = []
    snap = datetime.utcnow().strftime("%Y-%m-%d")
    for e in data["_embedded"]["events"]:
        venues = e.get("_embedded", {}).get("venues", [{}])
        v = venues[0] if venues else {}
        attractions = e.get("_embedded", {}).get("attractions", [{}])
        a = attractions[0] if attractions else {}
        c = (e.get("classifications") or [{}])[0]
        price = (e.get("priceRanges") or [{}])[0]

        rows.append({
            "id": e.get("id"),
            "name": e.get("name"),
            "url": e.get("url"),
            "type": e.get("type"),
            "locale": e.get("locale"),
            "date": e.get("dates", {}).get("start", {}).get("localDate"),
            "time": e.get("dates", {}).get("start", {}).get("localTime"),
            "status": e.get("dates", {}).get("status", {}).get("code"),
            "onsale_date": e.get("sales", {}).get("public", {}).get("startDateTime"),
            "offsale_date": e.get("sales", {}).get("public", {}).get("endDateTime"),
            "venue": v.get("name"),
            "venue_id": v.get("id"),
            "city": (v.get("city") or {}).get("name"),
            "state": (v.get("state") or {}).get("name"),
            "country": (v.get("country") or {}).get("name"),
            "venue_lat": (v.get("location") or {}).get("latitude"),
            "venue_lon": (v.get("location") or {}).get("longitude"),
            "artist": a.get("name"),
            "artist_id": a.get("id"),
            "segment": (c.get("segment") or {}).get("name"),
            "genre": (c.get("genre") or {}).get("name"),
            "subgenre": (c.get("subGenre") or {}).get("name"),
            "family": c.get("family"),
            "min_price": price.get("min"),
            "max_price": price.get("max"),
            "currency": price.get("currency"),
            "snapshot_date": snap,
        })
    return pd.DataFrame(rows)

def fetch_all_for_window(start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    params = {
        # classificationName is cleaner than keyword for music:
        "classificationName": "Music",
        "sort": "date,asc",
        "startDateTime": iso_utc(start_dt),
        "endDateTime": iso_utc(end_dt),
        # optional country filter to reduce noise:
        # "countryCode": "US",
    }
    first = fetch_page(page=0, **params)
    if "_embedded" not in first:
        return pd.DataFrame()
    total_pages = int(first["page"]["totalPages"])
    dfs = [parse_events_data(first)]
    for pg in range(1, total_pages):
        try:
            data = fetch_page(page=pg, **params)
            dfs.append(parse_events_data(data))
            time.sleep(0.2)  # be polite
        except requests.HTTPError as e:
            print(f"Page {pg} failed: {e}")
            break
    return pd.concat(dfs, ignore_index=True).drop_duplicates(subset=["id"])

def fetch_across_months(start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    chunks = []
    for s, e in month_windows(start_dt, end_dt):
        print(f"Fetching {s.date()} → {e.date()} ...")
        df = fetch_all_for_window(s, e)
        if not df.empty:
            chunks.append(df)
    if not chunks:
        return pd.DataFrame()
    return pd.concat(chunks, ignore_index=True).drop_duplicates(subset=["id"])

# --------- main ---------
def main():
    now = datetime.utcnow()
    start = now
    end = now + timedelta(days=90)  # next 3 months

    df_new = fetch_across_months(start, end)
    if df_new.empty:
        print("⚠️ No data fetched.")
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(OUT_FILE):
        old = pd.read_parquet(OUT_FILE)
        combined = pd.concat([old, df_new], ignore_index=True)
        # keep one row per (event id, snapshot_date)
        combined = combined.drop_duplicates(subset=["id", "snapshot_date"])
    else:
        combined = df_new

    combined.to_parquet(OUT_FILE, index=False)
    print(f"✅ Wrote {len(df_new)} new rows (total {len(combined)}) → {OUT_FILE}")

if __name__ == "__main__":
    main()
