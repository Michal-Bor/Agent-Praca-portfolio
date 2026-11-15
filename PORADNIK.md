## Pokaz w dwie minuty

1. W **Ofertach** wybierz **Zobacz ofertę**. Wyszukiwarka i filtr pomagają zawęzić listę.
2. W **Dopasowaniu** przeczytaj mocne strony oraz braki. Oceny są gotowymi przykładami, a nie obietnicą zatrudnienia.
3. Otwórz **Dokumenty**, wybierz CV, list lub pytania na rozmowę. W trybie **Edycja** zmień fragment i kliknij **Zapisz nową wersję**.
4. Wróć do **Podglądu**, wybierz zapisaną wersję i pobierz TXT, DOCX lub PDF. Notatki do dokumentu nie trafiają do pliku.
5. Zmień **Etap rekrutacji**, a w **Notatkach** zapisz ustalenia i datę. Sekcja **Moje aplikacje** pokazuje oferty ze statusem innym niż „nowa”.
6. Przycisk **Zresetuj pokaz** przywraca przykłady i usuwa zmiany z Twojej sesji.

Dane osób, firm, ogłoszeń i wynagrodzeń są fikcyjne. Każdy odwiedzający ma własną sesję w pamięci serwera. Przeładowanie strony lub restart serwera może usunąć zmiany. Nie wpisuj danych prywatnych. Data przypomnienia nie uruchamia powiadomień. Aplikacja nie wysyła zgłoszeń ani wiadomości.

## Co przedstawia projekt

Agent Praca pomaga przejść od ogłoszenia do przygotowanej aplikacji: porządkuje oferty, pokazuje dopasowanie do profilu, wspiera przygotowanie dokumentów i śledzenie rekrutacji. Ostateczną treść sprawdza użytkownik i samodzielnie wysyła aplikację.

| Obszar | Publiczny pokaz | Pełna aplikacja lokalna |
|---|---|---|
| Oferty i profil | Stałe, fikcyjne przykłady | Własny profil, dodawanie ofert, źródła RSS i wyszukiwanie AI |
| Ocena i dokumenty | Wcześniej przygotowane przykłady | Claude API po uruchomieniu zadania przez użytkownika |
| Zapis | Pamięć osobnej sesji | Baza SQLite i pliki na komputerze |
| Edycja i eksport | Wersje dokumentów, TXT, DOCX i PDF | Edycja, kontrola treści i eksport |
| Koszty API | Brak wywołań API | Wyłącznik AI, limity i ewidencja użycia |

## Jak zbudowano publiczny pokaz

- **Python i Streamlit** odpowiadają za widoki, formularze i nawigację.
- `portfolio_app.py` inicjuje osobną sesję i wybiera stronę.
- `portfolio_data.py` tworzy świeżą kopię fikcyjnych danych i sprawdza zapisywane wersje dokumentu.
- `portfolio_ui.py` obsługuje filtrowanie, statusy, notatki i dokumenty. Zmiany trafiają do `st.session_state`, bez wspólnej bazy i plików użytkowników.
- `dokumenty.py` oddziela treść dokumentu od notatek, a `eksport.py` tworzy pliki przez **python-docx** i **fpdf2**. Moduły pochodzą z pełnej aplikacji; eksport w pokazie nie importuje prywatnej konfiguracji.
- Automatyczne testy sprawdzają m.in. izolację sesji, historię dokumentów, eksport i działanie interfejsu.

Przepływ pokazu: **fikcyjne dane → widoki Streamlit → zmiany w sesji → eksport pliku**.

## Jak działa pełna aplikacja

Wersja lokalna ma dodatkową warstwę agenta (`agent.py`): dobiera narzędzia do zadania, korzysta z Claude API i zapisuje wyniki w SQLite (`db.py`). Profil oraz kontrole treści obsługuje `moj_profil.py`. Edytor profilu, kopie zapasowe i źródła ofert są osobnymi modułami. Kontrole faktów to reguły pomocnicze; nie zastępują przeczytania dokumentu.

Publiczne repozytorium zawiera kod pokazu. Prywatna baza, CV, klucze API i kopie zapasowe nie są publikowane. Pokaz nie importuje klienta AI, nie wczytuje `.env` i nie potrzebuje żadnych sekretów.

## Krótki opis do portfolio

**Agent Praca — asystent organizacji poszukiwania pracy w Pythonie i Streamlit.** Projekt obejmuje dopasowanie ofert do profilu, przygotowanie materiałów rekrutacyjnych, wersjonowanie dokumentów i śledzenie etapów rekrutacji. Pełna wersja integruje Claude API i SQLite. Publiczne demo działa na fikcyjnych danych, bez płatnych wywołań AI, z osobnym stanem każdego odwiedzającego oraz eksportem DOCX, PDF i TXT.
