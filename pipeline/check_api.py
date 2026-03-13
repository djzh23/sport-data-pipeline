import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")

r = requests.get(
    "https://api.football-data.org/v4/competitions/BL1/matches?season=2025",
    headers={"X-Auth-Token": API_KEY}
)

data = r.json()
matches = data["matches"]
finished = [m for m in matches if m["status"] == "FINISHED"]

print(f"Gesamt Spiele in API: {len(matches)}")
print(f"Davon gespielt: {len(finished)}")
print(f"Spieltage: {sorted(set(m['matchday'] for m in finished))}")
