"""Podział zapisanego dokumentu na treść do wysłania i notatki dla użytkownika (bez AI).

Szkic CV kończy się notatkami („Zmiany względem oryginału”, „Czego brakuje względem oferty”), które NIE są częścią
dokumentu do wysłania. Notatki zaczynają się wyłącznie od:
1. jawnego znacznika – linii w rodzaju „----- NOTATKI DLA CIEBIE (nie wysyłaj) -----” (tak pisze teraz agent), albo
2. linii z samych myślników (co najmniej 5), po której pierwszym niepustym wierszem jest znany nagłówek notatek
   (zapis starszych szkiców).
Zwykła linia „-----” w środku dokumentu (np. ozdobny separator dodany przy poprawkach) NICZEGO nie ucina.
Ostrzeżenia kontroli, uzasadnienia AI, historia zmian i dane techniczne nie są w ogóle częścią treści dokumentu –
aplikacja trzyma je osobno, więc nie trafiają do eksportu."""
import re

NOTES_MARKER = "----- NOTATKI DLA CIEBIE (nie wysyłaj) -----"
_MARKER_RE = re.compile(r"^[ \t]*[-=]{3,}[ \t]*NOTATKI\b[^\n]*$", re.IGNORECASE | re.MULTILINE)
_DASHES_RE = re.compile(r"^[ \t]*-{5,}[ \t]*$", re.MULTILINE)
_NOTES_HEADINGS = re.compile(
    r"^[\s*#_>]*(?:zmiany\s+względem|czego\s+brakuje|notatki\b|uwagi\s+dla\s+ciebie|do\s+usunięcia\s+przed\s+wysłaniem"
    r"|braki\s+względem\s+oferty)", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\[DO UZUPEŁNIENIA[^\]]*\]", re.IGNORECASE)


def split_document(content):
    """Zwraca {"tresc": treść do wysłania, "notatki": notatki (albo ""), "znacznik": linia podziału albo None}.
    Bez rozpoznanego początku notatek cały tekst jest treścią do wysłania."""
    text = (content or "").replace("\r\n", "\n")
    marker = _MARKER_RE.search(text)
    if marker:
        return {"tresc": text[:marker.start()].rstrip(), "notatki": text[marker.end():].strip(),
                "znacznik": marker.group(0).strip()}
    for m in _DASHES_RE.finditer(text):
        following = next((line for line in text[m.end():].split("\n") if line.strip()), "")
        if _NOTES_HEADINGS.match(following):
            return {"tresc": text[:m.start()].rstrip(), "notatki": text[m.end():].strip(),
                    "znacznik": m.group(0).strip()}
    return {"tresc": text.strip(), "notatki": "", "znacznik": None}


def content_to_send(content):
    return split_document(content)["tresc"]


def placeholders(text):
    """Miejsca [DO UZUPEŁNIENIA: …], które trzeba uzupełnić przed wysłaniem."""
    return PLACEHOLDER_RE.findall(text or "")
