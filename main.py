from pipeline.extract import get_all_matches
from pipeline.transform import load_data, add_match_results, build_standings
from pipeline.load import save_to_db, query_db

# -- Extract (API aufrufen & CSV speichern) --
print("Lade Bundesliga Saison 2024/25 von API...")
raw_df = get_all_matches("BL1", "2025")
raw_df.to_csv("data/bundesliga_2024.csv", index=False)
print(f"CSV gespeichert mit {len(raw_df)} Zeilen ✓")

# -- Transform --
df = load_data()
df = add_match_results(df)
standings = build_standings(df)

# -- Load --
save_to_db(df, "matches")
save_to_db(standings.reset_index(), "standings")

# -- SQL Abfragen --
print("\n=== Top 5 Torreichste Spiele ===")
print(query_db("""
    SELECT home_team, away_team, home_goals, away_goals, total_goals
    FROM matches
    ORDER BY total_goals DESC
    LIMIT 5
"""))

print("\n=== Tabelle Top 5 ===")
print(query_db("""
    SELECT team, played, points, wins, draws, losses, goal_diff
    FROM standings
    ORDER BY points DESC, goal_diff DESC
    LIMIT 5
"""))
