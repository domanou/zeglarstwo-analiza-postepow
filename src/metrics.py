import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "zeglarstwo.db")

def get_season_range(available_years):
    min_year = min(available_years)
    max_year = max(available_years)

    print(f"Dostępne sezony w bazie {min_year}-{max_year}")
    print("Wybierz zakres sezonów (naciśnij ENTER, aby wybrać wszystkie):")

    start_year_input = input(
        f"Rok początkowy [{min_year}]"
    ).strip()
    end_year_input = input(
        f"Rok końcowy [{max_year}]"
    ).strip()

    start_year = int(start_year_input) if start_year_input else min_year
    end_year = int(end_year_input) if end_year_input else max_year
    return start_year, end_year

def apply_drops(df, drops_count):
    """Usuwa N najgorszych wyników (najniższy wskaźnik Normalizacji) dla każdego zawodnika."""
    if drops_count <= 0:
        return df

        # Wyszukujemy indeksy N najgorszych wyników dla każdego zawodnika
    worst_indices = (
        df.sort_values("Normalizacja", ascending=True)
        .groupby("Zawodnik")
        .head(drops_count)
        .index
    )

    # Odrzucamy te indeksy z oryginalnej ramki danych
    return df.drop(index=worst_indices)

def calculate_metrics():
    "Oblicza odchylenie standardowe, wskazuje najgorszy i najlepszy wynik, dodaje możliwość podziału wyników na sezony"
    if not os.path.exists(DB_PATH):
        print(f"{DB_PATH} nie istnieje. Uruchom etl.py.")
        return
    conn = sqlite3.connect(DB_PATH)
    query = "select * from Wyniki_Regat"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["Data_rozpoczecia"] = pd.to_datetime(df["Data_rozpoczecia"])
    df["Rok"] = df["Data_rozpoczecia"].dt.year

    available_years = df["Rok"].dropna().unique()
    start_year, end_year = get_season_range(available_years)
    df = df[(df["Rok"] >= start_year) & (df["Rok"] <= end_year)]

    if df.empty:
        print(f"Brak startów w latach {start_year}-{end_year}")
        return

    drops_input = input("\n Ile najgorszych wyników odrzucić? [0]: ").strip()
    drops_count = int(drops_input) if drops_input.isdigit() else 0

    if drops_count > 0:
        df = apply_drops(df, drops_count)

    stats_df = df.groupby("Zawodnik")["Normalizacja"].agg(
        Liczba_startow = "count",
        Srednia = "mean",
        Mediana = "median",
        Odchylenie_standardowe = "std",
        Najlepszy_wynik = "max",
        Najgorszy_wynik = "min"
    ).reset_index()

    stats_df["CV"] = stats_df["Odchylenie_standardowe"]/stats_df["Srednia"]

    stats_df = stats_df.round(3)

    print(f"\n=== PODSUMOWANIE STATYSTYCZNE ZAWODNIKÓW W LATACH {start_year}-{end_year} ===")
    print(stats_df.to_string(index=False))

if __name__ == "__main__":
    calculate_metrics()
