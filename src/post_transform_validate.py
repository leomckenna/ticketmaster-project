import argparse, sqlite3, pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--db", required=True)
args = p.parse_args()

con = sqlite3.connect(args.db)
q = lambda sql, **k: pd.read_sql(sql, con, **k)

import pandas as pd

# list user tables 
tables = pd.read_sql("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
""", con)["name"].tolist()

rows = []
for t in tables:
    n = pd.read_sql(f'SELECT COUNT(*) AS rows FROM "{t}";', con).loc[0, "rows"]
    rows.append({"name": t, "rows": n})

row_counts = pd.DataFrame(rows).sort_values("name").reset_index(drop=True)
print("\n== Row counts ==")
print(row_counts.to_string(index=False))


print("\n== Null rates on key columns ==")
print(q("""
SELECT 'events' AS tbl,
  SUM(event_id IS NULL)*1.0/COUNT(*) AS p_null_id,
  SUM(datetime IS NULL)*1.0/COUNT(*) AS p_null_datetime
FROM events
UNION ALL
SELECT 'event_price_history',
  SUM(event_id IS NULL)*1.0/COUNT(*),
  SUM(snapshot_date IS NULL)*1.0/COUNT(*)
FROM event_price_history
UNION ALL
SELECT 'venues',
  SUM(venue_id IS NULL)*1.0/COUNT(*),
  NULL
FROM venues
UNION ALL
SELECT 'artists',
  SUM(artist_id IS NULL)*1.0/COUNT(*),
  NULL
FROM artists
""").to_string(index=False))


print("\n== Uniqueness checks ==")
print(q("""
SELECT 'events'              AS table_name,
       'event_id'            AS key_fields,
       COUNT(*)              AS total_rows,
       COUNT(DISTINCT event_id) AS distinct_keys,
       COUNT(*) - COUNT(DISTINCT event_id) AS duplicate_keys
FROM events
UNION ALL
SELECT 'venues'              AS table_name,
       'venue_id'            AS key_fields,
       COUNT(*),
       COUNT(DISTINCT venue_id),
       COUNT(*) - COUNT(DISTINCT venue_id)
FROM venues
UNION ALL
SELECT 'artists'             AS table_name,
       'artist_id'           AS key_fields,
       COUNT(*),
       COUNT(DISTINCT artist_id),
       COUNT(*) - COUNT(DISTINCT artist_id)
FROM artists
UNION ALL
SELECT 'event_price_history' AS table_name,
       '(event_id, snapshot_date)' AS key_fields,
       COUNT(*),
       COUNT(DISTINCT event_id || '|' || COALESCE(CAST(snapshot_date AS TEXT),'')),
       COUNT(*) - COUNT(DISTINCT event_id || '|' || COALESCE(CAST(snapshot_date AS TEXT),''))
FROM event_price_history;
""").to_string(index=False))


print("\n== Foreign-key coverage (orphans) ==")
print(q("""
SELECT 'events.artist_id→artists' AS fk,
  SUM(NOT EXISTS (SELECT 1 FROM artists a WHERE a.artist_id=e.artist_id))*1.0/COUNT(*) AS p_orphans
FROM events e
UNION ALL
SELECT 'events.venue_id→venues',
  SUM(NOT EXISTS (SELECT 1 FROM venues v WHERE v.venue_id=e.venue_id))*1.0/COUNT(*)
FROM events e
""").to_string(index=False))


print("\n== Currencies & min_price sanity ==")
print(q("""
SELECT
  COALESCE(currency,'(NULL)')                 AS currency,
  COUNT(*)                                    AS total_rows,
  1.0*SUM(min_price IS NULL)/COUNT(*)         AS min_price_null_rate,
  1.0*SUM(min_price < 0)/COUNT(*)             AS min_price_negative_rate,
  1.0*SUM(min_price = 0)/COUNT(*)             AS min_price_zero_rate
FROM event_price_history
GROUP BY currency
ORDER BY total_rows DESC;
""").to_string(index=False))

con.close()
print("Validation complete.")
