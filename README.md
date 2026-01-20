# Ticketmaster Event Data Pipeline
This project is an end-to-end data engineering pipeline that collects real-time event data from the Ticketmaster API, processes and stores it in a database for long-term access, and enables downstream exploratory data analysis (EDA) to uncover key insights.

## Overview
- Read data from the Ticketmaster API
- Normalize and structure the data into relational tables
- Load and persist the data in a SQL database
- Orchestrate extraction → transform → load using a pipeline script
- Perform EDA to derive insights from the stored data

## Structure
<<<<<<< Updated upstream


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

=======
```
.
├── .github/
│   └── workflows/
│       └── tm_snapshot.yml        # GitHub Actions workflow for daily snapshots
├── data/
│   └── .gitkeep                   # Ensures folder exists
├── src/
│   ├── db/
│   │   ├── Load.py                # Load normalized tables into SQLite
│   │   └── schema.sql             # Database schema definition
│   │
│   ├── Analysis_python/
│   │   └── analysis_EDA.ipynb     # EDA, mainly focusing on ticket prices
│   │   └── analysis_viz.ipynb     # Viz
│   ├── Analysis_r/
|   |
│   ├── config.py                  # Config paths/constants (e.g. dirs, file names)
│   ├── main.py                    # End-to-end transform + load pipeline
│   ├── post_transform_validate.py # Sanity checks on normalized outputs
│   ├── ticketmaster_snapshot.py   # API extractor
│   └── Transform.py               # Raw to normalized relational CSVs
│
├── dockerfile_python              # Optional containerization for Python code
├── dockerfile_r                   # Optional containerization for R code
├── README.md
└──  requirements.txt
└──  install_packages.R
```
>>>>>>> Stashed changes

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
python src/main.py --data ./data/events_history.parquet --db events.db
```
| Flag | Description |
|------|-------------|
| `--data <path>` | Input raw events parquet file |
| `--db <path>` | Output SQLite database. Will be created if not present. Recommended at project root. |
| `--clean` | Optional. Remove intermediate normalized CSVs after successful load. |
<<<<<<< Updated upstream
=======

This will create the database, events.db. 

#### Run validation file
src/post_transform_validate.py

### 3. Run Analyses

#### Optional: Containerize with Docker

#### Python code

Steps:
- [ ] Build docker image: `docker build -f dockerfile-python -t analysis-python .`
- [ ] Run docker image: `docker run analysis-python`

This will open Jupyter Notebook, and you can run the analysis kernels yourself. 

#### R code

Steps:
- [ ] Build docker image: `docker build -f dockerfile-r -t analysis-r .`
- [ ] Run docker image: `docker run analysis-r`

This will execute the script for the creation of the RShiny dashboard. 

### Or: Skip containerization

Run the following analysis files:
- [ ] src/Analysis_python/analysis_EDA.ipynb
- [ ] src/Analysis_python/analysis_viz.ipynb
- [ ] src/Analysis_r/


## Author
```
Leo McKenna, Jill Cusick, Pengyun Wang, Xinyue Yan
```
>>>>>>> Stashed changes
