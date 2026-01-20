# Ticketmaster Event Data Pipeline
This project is an end-to-end data engineering pipeline that collects real-time event data from the Ticketmaster API, processes and stores it in a database for long-term access, and enables downstream exploratory data analysis (EDA) to uncover key insights.

## Overview
- Extract Ticketmaster event data via API
- Normalize and structure the data into relational tables
- Load structured tables into a SQLite database
- Perform EDA to derive insights from a prepared test dataset
- This project also includes a deployed interactive R Shiny dashboard

## Structure
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
│   │   └── analysis_EDA.ipynb     # EDA, focused mostly on ticket prices
│   │   └── analysis_viz.ipynb     # Viz
|   |
│   ├── config.py                  # Config paths/constants (e.g. dirs, file names)
│   ├── main.py                    # End-to-end transform + load pipeline
│   ├── post_transform_validate.py # Sanity checks on normalized outputs
│   ├── ticketmaster_snapshot.py   # API extractor
│   └── Transform.py               # Raw to normalized relational CSVs
│
├── dockerfile-python              # Optional containerization of Python files
├── README.md
└──  requirements.txt
```

## Usage

### 1. Extract Raw Ticketmaster Data
This pipeline uses the Ticketmaster Discovery API, filtered by `classificationName=Music`, to pull data: https://app.ticketmaster.com/discovery/v2/events.json. See the official docs for request parameters and authentication.

**Important**: Ticketmaster's API has strict rate limits per day/hour and only returns a rolling ~90-day window of future events. It provides no historical data or versioning.
- Running the extractor once either locally or manually via Github Actions will only fetch one snapshot of the next ~90 days of events. 
- Running the extractor daily is the only way to accumulate a historical dataset that captures changes in event details (new events, cancellations, price updates, venue/time updates, etc.).

#### Option A: Run Extractor Locally
1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Set Environment Variables    

Create a `.env` file at root and set the following variables.
```bash
TICKETMASTER_API_KEY="YOUR_REAL_KEY"
```

3. Run the Extract Script
```bash
python ticketmaster_snapshot.py
```
This will fetch the latest 90-day “Music” events and append them to ```data/events_history.parquet``` with a `snapshot_date`. If the file does not exist, it will be created. Multiple manual runs on the same day will not pull more data.


#### Option B: Automated Extractor via Github Actions
1. Fork/clone this repo into your own GitHub account
2. Add your API key under Settings → Secrets and variables → Actions → New secret ```TICKETMASTER_API_KEY```
3. To run **daily**, edit ```.github/workflows/tm_snapshot.yml``` and uncomment
    ```
    schedule:
    - cron: "0 7 * * *"
    ```
    Then push the edited workflow file. GitHub will automatically run the extractor every day at 7:00 UTC. (Extracting on push is disabled by default.)

    To disable daily run, keep all triggers (```schedule:```, ```push:```) commented out, and push the changes. 
4. To run **manually**, go to GitHub → Actions → Ticketmaster Daily Snapshot → Run workflow.

    This will fetch the latest 90-day “Music” events and append them to ```data/events_history.parquet``` with a `snapshot_date`. If the file does not exist, it will be created. Multiple manual runs on the same day will not pull more data.

### 2. Transform and Load

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Run Data Pipeline Locally
```bash
python src/main.py --data ./data/events_history.parquet --db events.db
```
| Flag | Description |
|------|-------------|
| `--data <path>` | Input raw events parquet file |
| `--db <path>` | Output SQLite database. Will be created if not present. Recommended at project root. |
| `--clean` | Optional. Remove intermediate normalized CSVs after successful load. |

This will create or update the database named "events.db". 

#### Validate the Database (Optional)
```
python src/post_transform_validate.py
```
This prints a summary of table row counts and null-rate checks to help verify the integrity of the transformed data.


### 3. Data Analysis

The analyses are performed using the "events.db" SQLite database. All analysis notebooks are located in `src/Analysis_python/`.

#### Option A: Run in Docker

1. Install and open Docker Desktop.

2. Build the Docker image
```bash
docker build -f dockerfile-python -t analysis-python .
```

3. Run the container
```bash
docker run -p 8888:8888 analysis-python
```

Then open `http://127.0.0.1:8888` in your browser and run the analysis notebooks in Jupyter.

#### Option B: Run locally 

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Run analysis notebooks


#### Dashboard (R Shiny)

This project also includes a deployed interactive R Shiny dashboard for exploring Ticketmaster event data and analytics. This dashboard is based on API data collected between November 3, 2025 and November 11, 2025.

Live App: https://leomckenna.shinyapps.io/ticketmaster-api-dashboard/


## Author
Leo McKenna, Jill Cusick, Pengyun Wang, Xinyue Yan
