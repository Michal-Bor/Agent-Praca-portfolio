# Agent Praca — portfolio

Interaktywny pokaz asystenta poszukiwania pracy. Porównaj fikcyjne oferty, sprawdź przykładowe dopasowanie, popraw dokumenty i zapisz etap rekrutacji.

**Dane są fikcyjne; oceny i szkice przygotowano wcześniej. Demo nie uruchamia AI.**

## Uruchomienie

Python 3.12–3.14. Z katalogu repozytorium:

```sh
python -m pip install -r requirements.txt
python -m streamlit run portfolio_app.py
```

Nie potrzebujesz `.env`, klucza API ani bazy danych. Na Linuxie eksport PDF wymaga czcionki DejaVu Sans (`fonts-dejavu-core`; na Streamlit Cloud instaluje ją `packages.txt`).

## Instrukcja i architektura

[Poradnik obsługi i opis budowy](PORADNIK.md) — także w menu aplikacji.

Projekt publiczny jest osobnym pokazem pełnej aplikacji lokalnej. Używa fikcyjnych danych i pamięci sesji zamiast prywatnego profilu, klienta AI i bazy SQLite. Każda sesja ma niezależne statusy, notatki i wersje dokumentów. Zmiany mogą zniknąć po ponownym połączeniu lub restarcie. Nie ma funkcji wysyłania aplikacji ani powiadomień.

## Testy

```sh
python -m unittest discover -s tests -v
```

Testy są offline: izolacja sesji, edycja i eksport dokumentów oraz interakcje Streamlit. GitHub Actions wykonuje je na Linuxie.

## Wdrożenie na Streamlit Community Cloud

Repozytorium: `Michal-Bor/Agent-Praca-portfolio`, gałąź `main`, plik `portfolio_app.py`. Wybierz Python 3.14. Sekrety nie są potrzebne.
