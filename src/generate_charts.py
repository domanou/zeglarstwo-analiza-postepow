import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from metrics import apply_drops
from metrics import get_season_range

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "zeglarstwo.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(ASSETS_DIR, exist_ok=True)


def get_window_size():
    """Pobiera od użytkownika rozmiar okna średniej kroczącej (1-10)."""
    user_input = input(
        "\n1. Podaj liczbę startów do średniej kroczącej (1-10) [domyślnie: 10]: "
    ).strip()
    if not user_input:
        return 10
    try:
        val = int(user_input)
        return val if 1 <= val <= 10 else 10
    except ValueError:
        return 10


def get_participant_filter():
    """Pobiera filtr dotyczący liczby uczestników regat."""
    print("\n2. Wybór filtru liczby uczestników regat:")
    print("   [1] Wszystkie regaty (brak filtru)")
    print("   [2] Tylko ogólnopolskie regaty (powyżej 50 zawodników)")
    print("   [3] Tylko kregionalne regaty (50 i mniej zawodników)")
    choice = input("   Wybierz opcję (1-3) [domyślnie: 1]: ").strip()

    if choice == "2":
        return "above_50"
    elif choice == "3":
        return "below_equal_50"
    return "all"


def get_excluded_regattas(filtered_df, regatta_col):
    """Wyświetla listę regat (przefiltrowaną wstępnie wg liczby uczestników) i umożliwia wykluczenie pozycjonalne."""
    print("\n3. Czy chcesz wykluczyć konkretne regaty z obecnej listy?")
    choice = input("   [T/N]: ").strip().lower()

    if choice != "t":
        return []

    # Pobranie unikalnych regat z przefiltrowanego już DataFrame
    regatta_info = (
        filtered_df[[regatta_col, "Liczba_uczestnikow"]]
        .drop_duplicates()
        .dropna(subset=[regatta_col])
    )
    regatta_info = regatta_info.sort_values(by=regatta_col)

    if regatta_info.empty:
        print("  Brak regat spełniających kryteria w bazie.")
        return []

    print("\n   Dostępne regaty (po uwzględnieniu filtru liczby uczestników):")
    regattas_list = []
    for idx, (_, row) in enumerate(regatta_info.iterrows(), 1):
        name = row[regatta_col]
        participants = int(row["Liczba_uczestnikow"])
        regattas_list.append(name)
        print(f"   [{idx}] {name} ({participants} zawodników)")

    user_input = input(
        "\nPodaj numery regat do wykluczenia rozdzielone przecinkami (np. 1, 4): "
    ).strip()

    if not user_input:
        return []

    excluded = []
    for part in user_input.split(","):
        try:
            num = int(part.strip())
            if 1 <= num <= len(regattas_list):
                excluded.append(regattas_list[num - 1])
        except ValueError:
            continue

    if excluded:
        print(f"   Wykluczono: {', '.join(excluded)}")
    return excluded


def generate_chart():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Brak bazy danych w {DB_PATH}. Uruchom wpierw src/etl.py!"
        )

    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM Wyniki_Regat"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["Data_rozpoczecia"] = pd.to_datetime(df["Data_rozpoczecia"])
    df["Rok"] = df["Data_rozpoczecia"].dt.year

    available_years = df["Rok"].dropna().unique()
    if len(available_years) > 0:
        start_year, end_year = get_season_range(available_years)
        df = df[(df["Rok"] >= start_year) & (df["Rok"] <= end_year)]

    if df.empty:
        print(f" Brak startów w wybranym zakresie lat!")
        return

    # Określenie kolumny z nazwą regat
    regatta_col = (
        "Nazwa_regat_clean"
        if "Nazwa_regat_clean" in df.columns
        and df["Nazwa_regat_clean"].notna().any()
        else "Nazwa_regat_raw"
    )

    # --- KONFIGURACJA FILTRÓW PRZEZ UŻYTKOWNIKA ---
    window_size = get_window_size()
    participant_filter = get_participant_filter()

    # --- FILTR 1: LICZBA UCZESTNIKÓW (nakładany przed stworzeniem listy) ---
    filter_label = ""
    if participant_filter == "above_50":
        df = df[df["Liczba_uczestnikow"] > 50]
        filter_label = " (Uczestnicy > 50)"
    elif participant_filter == "below_equal_50":
        df = df[df["Liczba_uczestnikow"] <= 50]
        filter_label = " (Uczestnicy ≤ 50)"

    if df.empty:
        print("Brak danych spełniających wybrany filtr liczby uczestników!")
        return

    # --- FILTR 2: WYKLUCZANIE KONKRETNYCH REGAT (z przefiltrowanej listy) ---
    excluded_regattas = get_excluded_regattas(df, regatta_col)
    if excluded_regattas:
        df = df[~df[regatta_col].isin(excluded_regattas)]

    if df.empty:
        print("Wykluczono wszystkie dostępne regaty! Brak danych do wykresu.")
        return

    # --- FILTR 3: WYKLUCZANIE NAJGORSZYCH WYNIKÓW ---
    drops_input = input("\n Ile najgorszych wyników odrzucić? [0]: ").strip()
    drops_count = int(drops_input) if drops_input.isdigit() else 0

    if drops_count > 0:
        df = apply_drops(df, drops_count)

    # Sortowanie pod średnią kroczącą
    df = df.sort_values(["Zawodnik", "Data_rozpoczecia"])

    # Obliczenie średniej kroczącej
    col_name = f"Srednia_kroczaca_{window_size}"
    df[col_name] = df.groupby("Zawodnik")["Normalizacja"].transform(
        lambda x: x.rolling(window=window_size, min_periods=1).mean()
    )

    # --- RYSOWANIE WYKRESU ---
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))

    sns.lineplot(
        data=df,
        x="Data_rozpoczecia",
        y=col_name,
        hue="Zawodnik",
        marker="o",
        linewidth=2.5,
    )

    plt.title(
        f"Porównanie postępów zawodników (Średnia z {window_size} startów){filter_label}",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Data regat")
    plt.ylabel("Znormalizowany wynik (1 - Miejsce/Uczestnicy)")
    plt.ylim(0, 1.05)
    plt.axhline(
        y=0.8,
        color="green",
        linestyle="--",
        alpha=0.5,
        label="Próg wysokich wyników (Top 20%)",
    )
    plt.legend(title="Zawodnik")
    plt.tight_layout()

    # Zapis
    chart_path = os.path.join(ASSETS_DIR, "porownanie_zawodnikow.png")
    plt.savefig(chart_path, dpi=300)
    print(f"\n Wykres zapisano w: {chart_path}")
    plt.show()


if __name__ == "__main__":
    generate_chart()


