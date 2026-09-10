# Analiza Postępów Zawodników w Regatach (Klasa Optimist)

Projekt analityczny służący do monitorowania i analizy rozwoju zawodników żeglarskich na podstawie znormalizowanych wyników regat.

## Cel Projektu
Wynik w regatach zależy od liczby startujących zawodników. Projekt przelicza pozycje na znormalizowany wskaźnik $1 - \frac{\text{Miejsce}}{\text{Uczestnicy}}$, co pozwala na porównywanie występów na przestrzeni lat (Year-over-Year).

---

## 🚀 Uruchomienie Wszystkich Etapów

### 🛠️ Etap 1: ETL i Baza Danych (`src/etl.py`)
- Odczyt danych z pliku Excel z podziałem na zawodników (arkusze).
- Ekstrakcja adresów URL do wyników regat z hiperłączy.
- Czyszczenie danych i obliczenie znormalizowanych wyników.
- Zapis do bazy danych **SQLite** (`data/zeglarstwo.db`).

### 📊 Etap 2: Metryki Statystyczne (`src/metrics.py`)
- Obliczanie kluczowych statystyk formy: średnia, mediana, odchylenie standardowe (stabilność), najlepszy i najgorszy wynik.
- Interaktywne filtrowanie danych pod kątem wybranych sezonów (zakres lat).

### 📈 Etap 3: Wizualizacja i Trend Formy (`src/generate_charts.py`)
- Wykresy średniej kroczącej (konfigurowalne okno 1–10 startów).
- Filtrowanie regat ze względu na liczbę uczestników (>50 lub ≤50 zawodników).
- Interaktywna opcja wykluczania wybranych regat ze statystyk.
- Automatyczny zapis wykresów w katalogu `assets/`.

---

## 💻 Wykonanie w Terminalu

Uruchom poszczególne kroki kolejno w terminalu:

```bash
# 1. Przetworzenie danych i utworzenie bazy SQLite
python src/etl.py

# 2. Wyliczenie statystyk i filtrowanie sezonów
python src/metrics.py

# 3. Wygenerowanie interaktywnych wykresów
python src/generate_charts.py
