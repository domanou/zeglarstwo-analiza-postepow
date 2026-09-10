import sqlite3
import pandas as pd
from metrics import apply_drops, DB_PATH

def analyze_single_regatta():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM Wyniki_Regat"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("Baza danych jest pusta")
        return

    #Przetworzenie daty i wyciągnięcie roku
    df["Data_rozpoczecia"] = pd.to_datetime(df["Data_rozpoczecia"])
    df["Rok"] = df["Data_rozpoczecia"].dt.year

