import duckdb
import pandas as pd

DB_PATH = "data/bundesliga.db"

def save_to_db(df: pd.DataFrame, table_name: str):
    con = duckdb.connect(DB_PATH)
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    print(f"Tabelle '{table_name}' gespeichert mit {len(df)} Zeilen ✓")
    con.close()

def query_db(sql: str) -> pd.DataFrame:
    con = duckdb.connect(DB_PATH)
    result = con.execute(sql).fetchdf()
    con.close()
    return result