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


    #Wyciągniecie unikalnych regat wraz z rokiem ich rozegrania
    regattas = (
        df[["Nazwa_regat_clean", "Link_wyniki", "Rok"]]
        .drop_duplicates()
        .sort_values(by = ["Rok", "Nazwa_regat_clean"], ascending = [False, True])
        .reset_index(drop = True)
    )

    print("\n--- REGATY DOSTĘPNE W BAZIE ---")
    for idx, row in regattas.iterrows():
        print(f"[{idx + 1}] {row['Nazwa_regat_clean']} {row['Rok']}")

    choice = input("\n Wybierz numer do analizy: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(regattas)):
        print("Nieprawidłowy wybór")
        return

    selected_regatta = regattas.loc[int(choice) - 1]
    selected_link = selected_regatta["Link_wyniki"]
    selected_name = selected_regatta["Nazwa_regat_clean"]
    selected_year = selected_regatta["Rok"]

    #Filtrowanie danych tylko dla wybranego linku
    regatta_df = df[df["Link_wyniki"] == selected_link].copy()

    #Opcjonalnie zastosowanie opdrzutek
    drops_input = input("Ile najgorszych wyników odrzucić z analizy [0]: ").strip()
    drops_count = int(drops_input) if drops_input.isdigit() else 0

    if drops_count > 0:
        regatta_df = apply_drops(regatta_df, drops_count)

    if regatta_df.empty:
        print("Brak wyników dla regat po zastosowaniu odrzutek")
        return

    #Prezentacja wyników
    print(f"Wyniki: {selected_name}, {selected_year}")

    summary = regatta_df[["Zawodnik", "Miejsce", "Liczba_uczestnikow", "Normalizacja"]].sort_values("Miejsce")
    print(summary.to_string(index = False))

if __name__ == "__main__":
    analyze_single_regatta()


