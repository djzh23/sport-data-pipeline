# KoraStics — Football Analytics Platform

A data engineering project that extracts live football match data from the [football-data.org API](https://www.football-data.org/), processes it through an ETL pipeline, and visualizes it in an interactive web dashboard built with Streamlit.

**Leagues supported:** Bundesliga · Premier League · La Liga

---

## Features

- **ETL Pipeline** — Extract → Transform → Load with DuckDB storage
- **Live Data** — Real match data fetched directly from the API
- **Interactive Dashboard** with 4 views:
  - Overview (KPIs, result distribution, goals per matchday)
  - League table with Champions League / Europa League / Relegation zones
  - Matchday-by-matchday results
  - Team analysis (goals, points progression, match history)
- **Dark / Light theme** toggle
- **3 leagues** switchable from the sidebar

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.x |
| Data extraction | `requests` + football-data.org API |
| Data processing | `pandas` |
| Database | DuckDB |
| Dashboard | Streamlit + Plotly |

---

## Project Structure

```
sport-data-pipeline/
├── dashboard/
│   └── app.py          # Streamlit dashboard (KoraStics)
├── pipeline/
│   ├── extract.py      # API data extraction
│   ├── transform.py    # Data transformation & standings
│   ├── load.py         # DuckDB persistence
│   └── check_api.py    # API validation utility
├── data/               # Generated at runtime (gitignored)
├── main.py             # ETL pipeline entry point
├── requirements.txt
└── .env.example
```

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/your-username/sport-data-pipeline.git
cd sport-data-pipeline
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure your API key**

Copy `.env.example` to `.env` and add your key (free registration at [football-data.org](https://www.football-data.org/client/register)):
```bash
cp .env.example .env
# Edit .env and set FOOTBALL_API_KEY=your_key
```

**5. Run the ETL pipeline** *(optional — dashboard fetches data live)*
```bash
python main.py
```

**6. Start the dashboard**
```bash
streamlit run dashboard/app.py
```

---

## How It Works

```
football-data.org API
        │
        ▼
  pipeline/extract.py     ← HTTP request, parses JSON into DataFrame
        │
        ▼
  pipeline/transform.py   ← adds result column, calculates standings
        │
        ▼
  pipeline/load.py        ← saves to DuckDB (matches + standings tables)
        │
        ▼
  dashboard/app.py        ← Streamlit UI reads & visualizes the data
```

The dashboard calls the API directly on load (with caching), so no prior pipeline run is required.

---

## License

MIT
