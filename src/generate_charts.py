import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "zeglarstwo.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(ASSETS_DIR, exist_ok=True)


def get_window_size():
    """Pobiera od użytkownika rozmiar okna średniej kroczącej (1-10)."""
    user_input = input(
        "Podaj liczbę startów do średniej kroczącej (1-10) [domyślnie: 10]: "
    ).strip()

    if not user_input:
        return 10

    try:
        val = int(user_input)
        if 1 <= val <= 10:
            return val
        print("⚠️ Liczba spoza zakresu 1-10. Ustawiam domyślnie 10.")
        return 10
    except ValueError:
        print("⚠️ Nieprawidłowy format. Ustawiam domyślnie 10.")
        return 10


def generate_chart(window_size):
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Brak bazy danych w {DB_PATH}. Uruchom wpierw src/etl.py!"
        )

    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM Wyniki_Regat"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["Data_rozpoczecia"] = pd.to_datetime(df["Data_rozpoczecia"])
    df = df.sort_values(["Zawodnik", "Data_rozpoczecia"])

    # Wyliczenie średniej kroczącej
    col_name = f"Srednia_kroczaca_{window_size}"
    df[col_name] = df.groupby("Zawodnik")["Normalizacja"].transform(
        lambda x: x.rolling(window=window_size, min_periods=1).mean()
    )

    # Rysowanie wykresu
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
        f"Porównanie postępów zawodników (Średnia krocząca z {window_size} startów)",
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

    # Zapis wykresu
    chart_path = os.path.join(ASSETS_DIR, "porownanie_zawodnikow.png")
    plt.savefig(chart_path, dpi=300)
    print(
        f"Wygenerowano wykres dla średniej z {window_size} startów -> {chart_path}"
    )
    plt.show()


if __name__ == "__main__":
    selected_window = get_window_size()
    generate_chart(selected_window)

