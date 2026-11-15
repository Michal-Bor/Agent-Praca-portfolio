"""Eksport zapisanej wersji dokumentu (CV, list, pytania) do DOCX i PDF – bez AI i bez internetu.

Eksportowana jest wyłącznie treść do wysłania (dokumenty.split_document): bez notatek dla użytkownika,
ostrzeżeń kontroli, uzasadnień AI i metadanych technicznych. Tekst idzie dokładnie z wybranej, zapisanej wersji
(także Twojej ręcznej korekty). Obsługiwany zapis: nagłówki „# …”, wiersze WIELKIMI LITERAMI jako nagłówki sekcji,
listy „- ” / „• ” / „1. ”, pogrubienia **tak**, linia z samych myślników jako pozioma linia, puste wiersze jako
odstęp między akapitami. Kolejne niepuste wiersze tworzą jeden akapit z podziałem wierszy (jak w podglądzie).

Zależności: python-docx (DOCX) i fpdf2 (PDF). PDF potrzebuje czcionki TrueType z polskimi znakami – aplikacja
szuka jej w systemie (Arial, Calibri, Segoe UI, DejaVu Sans) albo bierze ścieżkę z PDF_CZCIONKA w .env."""
import io
import os
import re
from pathlib import Path

import dokumenty

def env(name, default=None):
    """Only font settings; do not import the private application's configuration."""
    value = os.environ.get(name, "").strip()
    return value or default

HEADING1, HEADING2, BULLET, NUMBERED, PARAGRAPH, RULE, SPACE = "h1", "h2", "punkt", "numer", "akapit", "linia", "odstęp"
_BULLET_RE = re.compile(r"^(\s*)[-*•▪●]\s+(.*)$")
_NUMBER_RE = re.compile(r"^(\s*)(\d{1,2}[.)])\s+(.*)$")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_RULE_RE = re.compile(r"^\s*(?:-{3,}|_{3,}|\*{3,}|={3,})\s*$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


class ExportError(Exception):
    """Eksport się nie udał – komunikat dla użytkownika."""


def _is_caps_heading(line):
    letters = [c for c in line if c.isalpha()]
    return 3 <= len(letters) and len(line) <= 60 and line.upper() == line and any(c.isupper() for c in letters)


def blocks(text):
    """Tekst → lista bloków (rodzaj, treść[, poziom/numer]). Nie gubi ani nie dodaje słów."""
    result, paragraph = [], []

    def flush():
        if paragraph:
            result.append((PARAGRAPH, list(paragraph)))
            paragraph.clear()

    for raw in (text or "").split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush()
            if result and result[-1][0] != SPACE:
                result.append((SPACE, None))
            continue
        heading = _HEADING_RE.match(line.strip())
        bullet = _BULLET_RE.match(line)
        number = _NUMBER_RE.match(line)
        if _RULE_RE.match(line):
            flush()
            result.append((RULE, None))
        elif heading:
            flush()
            result.append((HEADING1 if len(heading.group(1)) == 1 else HEADING2, heading.group(2).strip()))
        elif bullet:
            flush()
            result.append((BULLET, bullet.group(2).strip(), 2 if len(bullet.group(1)) >= 2 else 1))
        elif number:
            flush()
            result.append((NUMBERED, number.group(3).strip(), number.group(2)))
        elif _is_caps_heading(line.strip().strip("*").strip()) and not paragraph:
            flush()
            result.append((HEADING2, line.strip().strip("*").strip()))
        else:
            paragraph.append(line.strip())
    flush()
    while result and result[-1][0] == SPACE:
        result.pop()
    while result and result[0][0] == SPACE:
        result.pop(0)
    return result


def runs(text):
    """Tekst akapitu → [(fragment, pogrubiony)]. Niesparowane ** zostają zwykłym tekstem."""
    parts, pos = [], 0
    for m in _BOLD_RE.finditer(text):
        if m.start() > pos:
            parts.append((text[pos:m.start()], False))
        parts.append((m.group(1), True))
        pos = m.end()
    if pos < len(text):
        parts.append((text[pos:], False))
    return [p for p in parts if p[0]]


def plain_text(text):
    """Tekst dokumentu bez znaczników formatowania – do porównania z treścią eksportu."""
    lines = []
    for block in blocks(text):
        kind, content = block[0], block[1]
        if kind in (PARAGRAPH,):
            lines += [_BOLD_RE.sub(r"\1", line) for line in content]
        elif kind in (HEADING1, HEADING2, BULLET):
            lines.append(_BOLD_RE.sub(r"\1", content))
        elif kind == NUMBERED:
            lines.append(block[2] + " " + _BOLD_RE.sub(r"\1", content))
    return lines


# ----- DOCX -----

def to_docx(content, title="Dokument"):
    """Bajty pliku .docx z treścią do wysłania (notatki i metadane pominięte)."""
    from docx import Document
    from docx.enum.text import WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    text = dokumenty.content_to_send(content)
    doc = Document()
    props = doc.core_properties
    props.title, props.author, props.last_modified_by = title, "", ""
    props.comments = props.subject = props.keywords = props.category = ""
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Cm(2)
        section.left_margin = section.right_margin = Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(4)
    for name, size in (("Heading 1", 18), ("Heading 2", 13)):
        style = doc.styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0x1E, 0x2A, 0x2F)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(10 if name == "Heading 2" else 0)
        style.paragraph_format.space_after = Pt(4)
        rpr = style.element.get_or_add_rPr()
        fonts = rpr.find(qn("w:rFonts"))
        if fonts is None:
            fonts = OxmlElement("w:rFonts")
            rpr.append(fonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            fonts.set(qn(attr), "Calibri")
        for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            fonts.attrib.pop(qn(attr), None)

    def add_runs(paragraph, line):
        for fragment, bold in runs(line):
            paragraph.add_run(fragment).bold = bold or None

    for block in blocks(text):
        kind = block[0]
        if kind == HEADING1:
            add_runs(doc.add_heading(level=1), block[1])
        elif kind == HEADING2:
            add_runs(doc.add_heading(level=2), block[1])
        elif kind == BULLET:
            p = doc.add_paragraph(style="List Bullet 2" if block[2] == 2 else "List Bullet")
            p.paragraph_format.space_after = Pt(2)
            add_runs(p, block[1])
        elif kind == NUMBERED:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.9)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            p.paragraph_format.space_after = Pt(2)
            p.add_run(block[2] + " ")
            add_runs(p, block[1])
        elif kind == PARAGRAPH:
            p = doc.add_paragraph()
            for i, line in enumerate(block[1]):
                if i:
                    p.add_run().add_break(WD_BREAK.LINE)
                add_runs(p, line)
        elif kind == RULE:
            p = doc.add_paragraph()
            border = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            for key, value in (("w:val", "single"), ("w:sz", "6"), ("w:space", "1"), ("w:color", "999999")):
                bottom.set(qn(key), value)
            border.append(bottom)
            p._p.get_or_add_pPr().append(border)
        elif kind == SPACE:
            continue  # odstęp daje space_after akapitów
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ----- PDF -----

_FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
    (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf"),
    (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ("/Library/Fonts/Arial Unicode.ttf", "/Library/Fonts/Arial Unicode.ttf"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
]


def pdf_font():
    """(zwykła, pogrubiona) – ścieżki czcionek TTF z polskimi znakami albo ExportError z instrukcją."""
    custom = env("PDF_CZCIONKA")
    if custom:
        bold = env("PDF_CZCIONKA_POGRUBIONA", custom)
        if Path(custom).is_file() and Path(bold).is_file():
            return custom, bold
        raise ExportError(f"Nie znaleziono czcionki z PDF_CZCIONKA ({custom}). Popraw ścieżkę w .env.")
    windir = os.environ.get("WINDIR")
    candidates = list(_FONT_CANDIDATES)
    if windir:
        candidates.insert(0, (os.path.join(windir, "Fonts", "arial.ttf"), os.path.join(windir, "Fonts", "arialbd.ttf")))
    for regular, bold in candidates:
        if Path(regular).is_file() and Path(bold).is_file():
            return regular, bold
    raise ExportError("Nie znaleziono czcionki z polskimi znakami do PDF. Wpisz w .env ścieżkę do pliku .ttf, np. "
                      "PDF_CZCIONKA=C:\\Windows\\Fonts\\arial.ttf (eksport DOCX działa bez tego).")


def to_pdf(content, title="Dokument"):
    """Bajty pliku .pdf (A4) z treścią do wysłania – automatyczne podziały stron, nagłówek nie zostaje sam na dole
    strony, długie akapity przenoszą się na kolejną stronę."""
    from fpdf import FPDF

    regular, bold = pdf_font()
    text = dokumenty.content_to_send(content)
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_margins(22, 20, 22)
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_font("Tekst", "", regular)
    pdf.add_font("Tekst", "B", bold)
    pdf.set_title(title)
    pdf.set_author("")
    pdf.set_creator("")
    pdf.set_text_color(30, 42, 47)
    pdf.add_page()
    line_h = 5.6
    left = pdf.l_margin

    def write_runs(line, size=11, base_bold=False):
        for fragment, is_bold in runs(line):
            pdf.set_font("Tekst", "B" if (is_bold or base_bold) else "", size)
            pdf.write(line_h if size <= 11 else size * 0.5, fragment)

    def keep_room(mm):
        if pdf.get_y() + mm > pdf.page_break_trigger:
            pdf.add_page()

    for block in blocks(text):
        kind = block[0]
        pdf.set_x(left)
        if kind in (HEADING1, HEADING2):
            size = 17 if kind == HEADING1 else 12.5
            pdf.ln(2 if kind == HEADING2 else 0)
            keep_room(size * 0.5 + 2 * line_h)  # nagłówek nie zostaje sam na dole strony
            pdf.set_x(left)
            write_runs(block[1], size, base_bold=True)
            pdf.ln(size * 0.5 + 1.5)
        elif kind in (BULLET, NUMBERED):
            indent = 5 if kind == BULLET and block[2] == 1 else 10
            marker = ("•" if kind == BULLET else block[2])
            keep_room(line_h)
            pdf.set_font("Tekst", "", 11)
            pdf.set_x(left + indent - (3.5 if kind == BULLET else 5.5))
            pdf.cell(5.5 if kind == NUMBERED else 3.5, line_h, marker)
            pdf.set_left_margin(left + indent + 1.5)
            pdf.set_x(left + indent + 1.5)
            write_runs(block[1])
            pdf.ln(line_h + 0.6)
            pdf.set_left_margin(left)
        elif kind == PARAGRAPH:
            for line in block[1]:
                pdf.set_x(left)
                write_runs(line)
                pdf.ln(line_h)
            pdf.ln(1.2)
        elif kind == RULE:
            keep_room(4)
            y = pdf.get_y() + 1.5
            pdf.set_draw_color(160, 160, 160)
            pdf.line(left, y, pdf.w - pdf.r_margin, y)
            pdf.ln(4)
        elif kind == SPACE:
            pdf.ln(1.8)
    return bytes(pdf.output())


def file_name(kind, offer_id, version_id=None, extension="docx"):
    """Nazwa pliku jak przy dotychczasowym pobieraniu .txt, np. cv_oferta_3.docx."""
    return f"{kind}_oferta_{offer_id}" + (f"_wersja_{version_id}" if version_id else "") + f".{extension}"
