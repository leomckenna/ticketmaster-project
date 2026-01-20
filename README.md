# Ticketmaster Event Data Pipeline
This project is an end-to-end data engineering pipeline that collects real-time event data from the Ticketmaster API, processes and stores it in a database for long-term access, and enables downstream exploratory data analysis (EDA) to uncover key insights.

## Overview
- Read data from the Ticketmaster API
- Normalize and structure the data into relational tables
- Load and persist the data in a SQL database
- Orchestrate extraction → transform → load using a pipeline script
- Perform EDA to derive insights from the stored data

## Structure


## Ticketmaster Music Events – Daily Snapshot

This repo snapshots **Ticketmaster _Music_ events** for the next 90 days, every day.
Each run appends to `data/events_history.parquet` and preserves a `snapshot_date`
so you can analyze how listings evolve over time.

## What gets collected?
- Event metadata: `id`, `name`, `url`, `date`, `time`, `status`
- Venue & location: `venue`, `city`, `state`, `country`, `venue_lat`, `venue_lon`
- Artist/attraction: `artist`, `artist_id`
- Classification: `segment`, `genre`, `subgenre`, `family`
- Price range (if present): `min_price`, `max_price`, `currency`
- `snapshot_date`: UTC date the snapshot was taken

> Scope: public Discovery API, filtered by `classificationName=Music`,
> month-by-month across the next 90 days.


## Usage

### Install dependencies
```bash
pip install -r requirements.txt
```

### Set Environment Variables
Create a `.env` file and set the following variables:
```bash
TICKETMASTER_API_KEY="YOUR_REAL_KEY"
DB_URI="sqlite:///ticketmaster.db"
```

### Run Data Pipeline
```bash
python -m src.dag.pipeline
```

