"""Fictional, offline showcase. No private files, API clients or shared mutable state."""
from copy import deepcopy

PROFILE = """# Anna Nowak
Profil fikcyjny — przykład portfolio

## Doświadczenie
Specjalistka obsługi klienta | Przykładowe Studio | 2022–2025
- Obsługa zapytań e-mailowych i telefonicznych.
- Prowadzenie zgłoszeń w CRM i aktualizowanie bazy wiedzy.
- Przygotowywanie zestawień w Excelu.

## Umiejętności
Obsługa klienta, CRM, Excel, komunikacja pisemna.
Język angielski: B2.

## Kierunek rozwoju
Analiza danych i automatyzacja — cele nauki, nie potwierdzone kompetencje.
"""
EXPECTATIONS = "Praca hybrydowa w Toruniu lub zdalna. Umowa o pracę. Bez aktywnej sprzedaży telefonicznej."
STATUSES = ("nowa", "do wysłania", "wysłana", "rozmowa", "oferta", "odmowa", "rezygnuję")
KINDS = ("CV pod ofertę", "List motywacyjny", "Pytania na rozmowę")


def new_state():
    """Create independent nested data for each visitor. Scores are authored examples."""
    samples = [
        (1, "Specjalistka / specjalista obsługi klienta", "Przykładowe Studio", "Toruń · hybrydowo", "7 000–8 500 zł brutto / mies.", 8,
         "Obsługa klientów przez e-mail i telefon, prowadzenie zgłoszeń w CRM i aktualizacja bazy wiedzy. Wymagania: doświadczenie w obsłudze klienta, angielski B2, Excel. Umowa o pracę; praca od poniedziałku do piątku.",
         ["Doświadczenie w obsłudze klienta", "CRM i Excel", "Angielski B2"],
         ["Do potwierdzenia: godziny pracy i dokładny zakres odpowiedzialności."], "do wysłania"),
        (2, "Młodsza analityczka / młodszy analityk danych", "Demo Analytics", "Zdalnie", "6 500–8 000 zł brutto / mies.", 5,
         "Tworzenie raportów i kontrola jakości danych. Wymagania: Excel, podstawy SQL i Power BI. Mile widziane pierwsze projekty analityczne. Umowa o pracę, praca zdalna w Polsce.",
         ["Doświadczenie w zestawieniach Excel", "Zgodność z kierunkiem rozwoju"],
         ["SQL i Power BI nie są potwierdzone w profilu.", "Cel nauki nie oznacza posiadania umiejętności."], "nowa"),
        (3, "Customer Success Specialist", "Przykładowy Produkt", "Zdalnie", "7 500–9 000 zł brutto / mies.", 7,
         "Wsparcie klientów oprogramowania, prowadzenie prezentacji produktu i onboarding. Wymagania: obsługa klienta, angielski B2 i komunikacja pisemna. Mile widziane doświadczenie SaaS. Umowa o pracę.",
         ["Komunikacja z klientami", "Angielski B2"],
         ["Brak potwierdzonego doświadczenia SaaS i prowadzenia prezentacji."], "rozmowa"),
        (4, "Konsultantka / konsultant sprzedaży", "Demo Kontakt", "Toruń · stacjonarnie", "5 000 zł brutto + prowizja / mies.", 3,
         "Aktywne pozyskiwanie klientów przez telefon i realizacja celów sprzedażowych. Praca zmianowa, umowa o pracę. Wynagrodzenie obejmuje podstawę i zmienną prowizję.",
         ["Doświadczenie w kontakcie telefonicznym"],
         ["Aktywna sprzedaż telefoniczna jest sprzeczna z preferencjami.", "Prowizja nie jest gwarantowanym wynagrodzeniem."], "rezygnuję"),
    ]
    offers = []
    for id_, title, company, location, salary, score, text, strengths, gaps, status in samples:
        letter = (f"# List motywacyjny — przykład\n\nSzanowni Państwo,\n\n"
                  f"aplikuję na stanowisko {title} w firmie {company}. "
                  "Mam doświadczenie w obsłudze zapytań klientów, prowadzeniu zgłoszeń w CRM "
                  "i przygotowywaniu zestawień w Excelu. Posługuję się angielskim na poziomie B2. "
                  "Chętnie omówię, które z tych doświadczeń odpowiadają potrzebom Państwa zespołu.\n\n"
                  "Z poważaniem,\nAnna Nowak\n\n"
                  "----- NOTATKI DLA CIEBIE (nie wysyłaj) -----\n"
                  "Dokument demonstracyjny, przygotowany wcześniej. Wszystkie osoby i firmy są fikcyjne.")
        questions = ("# Pytania na rozmowę — przykład\n\n"
                     "1. Jak wygląda wdrożenie nowej osoby?\n"
                     "2. Po czym oceniacie powodzenie w pierwszych trzech miesiącach?\n"
                     "3. Jakich narzędzi używa zespół?\n"
                     "4. Jakie są godziny pracy i kolejne etapy rekrutacji?")
        cv = PROFILE + f"\n## Cel aplikacji\nStanowisko: {title}.\n"
        offers.append(dict(id=id_, title=title, company=company, location=location,
                           salary=salary, score=score, text=text, strengths=strengths, gaps=gaps,
                           status=status, notes="", reminder=None,
                           documents={k: [v] for k, v in zip(KINDS, (cv, letter, questions))}))
    return deepcopy(offers)


def save_document(offer, kind, content):
    content = content.strip()
    if not content:
        raise ValueError("Dokument nie może być pusty.")
    if len(content) > 20000:
        raise ValueError("Dokument może mieć maksymalnie 20 000 znaków.")
    versions = offer["documents"][kind]
    if content == versions[-1]:
        return False
    if len(versions) >= 10:
        raise ValueError("W pokazie można zapisać 10 wersji dokumentu. Zresetuj pokaz, aby zacząć od nowa.")
    versions.append(content)
    return True
