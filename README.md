# Analiza Postępów Zawodników w Regatach (Klasa Optimist)

Projekt analityczny służący do monitorowania i analizy rozwoju zawodników żeglarskich na podstawie znormalizowanych wyników regat.

## Cel Projektu
Wynik w regatach zależy od liczby startujących zawodników. Projekt przelicza pozycje na znormalizowany wskaźnik $1 - \frac{\text{Miejsce}}{\text{Uczestnicy}}$, co pozwala na porównywanie występów na przestrzeni lat (Year-over-Year).

## 🛠️ Etap 1: ETL i Baza Danych
- Odczyt danych z Excela z podziałem na zawodników (arkusze).
- Ekstrakcja adresów URL do wyników regat z hiperłączy.
- Czyszczenie i normalizacja danych.
- Zapis do bazy danych **SQLite** (`data/zeglarstwo.db`).

## Jak uruchomić ETL?
```bash
python src/etl.py
