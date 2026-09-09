import os
import re
import sqlite3
import openpyxl
import pandas as pd


def extract_clean_name(raw_name):
    """Usuwa daty, lokalizacje i podwójne spacje z nazwy regat."""
    if not raw_name or pd.isna(raw_name):
        return ""
    clean = str(raw_name).split("|")[0].strip()
    clean = re.sub(r"\b202\d\b", "", clean).strip()
    return clean


def run_etl():
    excel_path = os.path.join("data", "Dane do analizy.xlsx")
    db_path = os.path.join("data", "zeglarstwo.db")

    if not os.path.exists(excel_path):
        print(f"Błąd: Nie znaleziono pliku {excel_path}")
        return

    wb = openpyxl.load_workbook(excel_path)
    all_rows = []

    # Iteracja po wszystkich arkuszach (zawodnikach)
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=False))

        # Pomijamy nagłówek (wiersz 0)
        for row in rows[1:]:
            data_start = row[0].value
            mc = row[1].value
            l_ucz = row[2].value

            # Sprawdzamy, czy wiersz nie jest pusty i czy mamy komplet wyników
            if data_start is None or mc is None or l_ucz is None:
                continue

            nazwa_regat = row[4].value
            link_wyniki = (
                row[4].hyperlink.target if row[4].hyperlink else "Brak"
            )

            all_rows.append(
                {
                    "Zawodnik": sheet_name,
                    "Data_rozpoczecia": pd.to_datetime(data_start),
                    "Miejsce": int(mc),
                    "Liczba_uczestnikow": int(l_ucz),
                    "Nazwa_regat_raw": nazwa_regat,
                    "Nazwa_regat_clean": extract_clean_name(nazwa_regat),
                    "Link_wyniki": link_wyniki,
                }
            )

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("Nie znaleziono prawidłowych danych w pliku Excel.")
        return

    # Obliczenia i transformacje
    df["Normalizacja"] = 1 - (df["Miejsce"] / df["Liczba_uczestnikow"])
    df = df.sort_values(["Zawodnik", "Data_rozpoczecia"])

    # Średnia krocząca z 3 ostatnich startów dla każdego zawodnika
    df["Srednia_kroczaca_3"] = df.groupby("Zawodnik")[
        "Normalizacja"
    ].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

    # Zapis do bazy danych SQLite
    conn = sqlite3.connect(db_path)
    df.to_sql("Wyniki_Regat", conn, if_exists="replace", index=False)
    conn.close()

    print(
        f"ETL zakończony sukcesem! Zapisano {len(df)} rekordów w bazie danych: {db_path}"
    )


if __name__ == "__main__":
    run_etl()
