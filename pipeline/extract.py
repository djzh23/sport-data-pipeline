import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

LEAGUES = {
    "Bundesliga 🇩🇪": {"code": "BL1", "season": "2025"},
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {"code": "PL", "season": "2025"},
    "La Liga 🇪🇸": {"code": "PD", "season": "2025"},
}

def get_all_matches(league_code: str, season: str) -> pd.DataFrame:
    url = f"{BASE_URL}/competitions/{league_code}/matches?season={season}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Fehler: {response.status_code} - {response.text}")
        return pd.DataFrame()

    matches = response.json()["matches"]

    rows = []
    for match in matches:
        rows.append({
            "matchday": match["matchday"],
            "home_team": match["homeTeam"]["name"],
            "away_team": match["awayTeam"]["name"],
            "home_goals": match["score"]["fullTime"]["home"],
            "away_goals": match["score"]["fullTime"]["away"],
            "status": match["status"],
            "date": match["utcDate"]
        })

    df = pd.DataFrame(rows)
    finished = len(df[df["status"] == "FINISHED"])
    print(f"{league_code} geladen: {len(df)} Spiele ({finished} gespielt)")
    return df
