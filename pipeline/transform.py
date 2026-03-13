import pandas as pd

def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/bundesliga_2024.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["status"] == "FINISHED"]
    return df

def add_match_results(df: pd.DataFrame) -> pd.DataFrame:
    def get_result(row):
        if row["home_goals"] > row["away_goals"]:
            return "home_win"
        elif row["home_goals"] < row["away_goals"]:
            return "away_win"
        else:
            return "draw"
    
    df["result"] = df.apply(get_result, axis=1)
    df["total_goals"] = df["home_goals"] + df["away_goals"]
    return df

def build_standings(df: pd.DataFrame) -> pd.DataFrame:
    teams = pd.concat([
        df[["home_team", "home_goals", "away_goals", "result"]].rename(
            columns={"home_team": "team", "home_goals": "scored", "away_goals": "conceded"}
        ).assign(is_home=True),
        df[["away_team", "away_goals", "home_goals", "result"]].rename(
            columns={"away_team": "team", "away_goals": "scored", "home_goals": "conceded"}
        ).assign(is_home=False)
    ], ignore_index=True)

    def get_points(row):
        if row["result"] == "home_win":
            return 3 if row["is_home"] else 0
        elif row["result"] == "away_win":
            return 0 if row["is_home"] else 3
        else:
            return 1

    teams["points"] = teams.apply(get_points, axis=1)
    teams["wins"] = teams.apply(
        lambda r: 1 if (r["result"] == "home_win" and r["is_home"]) or 
                      (r["result"] == "away_win" and not r["is_home"]) else 0, axis=1)
    teams["draws"] = (teams["result"] == "draw").astype(int)
    teams["losses"] = teams.apply(
        lambda r: 1 if (r["result"] == "away_win" and r["is_home"]) or 
                      (r["result"] == "home_win" and not r["is_home"]) else 0, axis=1)

    standings = teams.groupby("team").agg(
        played=("points", "count"),
        points=("points", "sum"),
        wins=("wins", "sum"),
        draws=("draws", "sum"),
        losses=("losses", "sum"),
        scored=("scored", "sum"),
        conceded=("conceded", "sum")
    ).reset_index()

    standings["goal_diff"] = standings["scored"] - standings["conceded"]
    standings = standings.sort_values(
        by=["points", "goal_diff", "scored"], 
        ascending=False
    ).reset_index(drop=True)
    standings.index += 1

    return standings