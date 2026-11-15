"""Visitor interactions; all mutable data stays in Streamlit session state."""
import streamlit as st
import dokumenty
import eksport
from portfolio_data import STATUSES, KINDS, save_document


def offers_page(applications=False):
    offers = st.session_state.offers
    selected = st.session_state.selected_offer
    if selected is not None:
        details(next(o for o in offers if o["id"] == selected))
        return
    st.title("Moje aplikacje" if applications else "Agent Praca")
    st.markdown("Porównaj oferty. Przygotuj dokumenty. Zapanuj nad rekrutacją.")
    st.info("Pokaz portfolio: fikcyjne ogłoszenia i wcześniej przygotowane oceny. Żadne AI nie jest tu uruchamiane.", icon=":material/info:")
    if not applications:
        with st.container(horizontal=True):
            st.metric("Przykładowe oferty", len(offers), border=True)
            st.metric("W toku", sum(o["status"] in ("do wysłania", "wysłana", "rozmowa") for o in offers), border=True)
        st.caption("Zacznij od pierwszej oferty: sprawdź dopasowanie, popraw dokument i zapisz etap rekrutacji.")
    query = st.text_input("Szukaj oferty", placeholder="Stanowisko, firma lub lokalizacja", key="search", max_chars=120)
    status = st.selectbox("Status", ["wszystkie", *STATUSES], key="filter_status")
    rows = [o for o in offers if (not applications or o["status"] != "nowa")
            and (status == "wszystkie" or o["status"] == status)
            and query.casefold() in f'{o["title"]} {o["company"]} {o["location"]}'.casefold()]
    if not rows:
        st.info("Brak ofert dla tych filtrów. Zmień wyszukiwanie lub status.")
    for offer in sorted(rows, key=lambda o: o["score"], reverse=True):
        with st.container(border=True):
            st.subheader(offer["title"])
            st.caption(f'{offer["company"]} · {offer["location"]}')
            st.write(offer["salary"])
            st.markdown(f'**Dopasowanie przykładowe: {offer["score"]}/10** · Status: {offer["status"]}')
            if st.button("Zobacz ofertę", key=f'open_{offer["id"]}', icon=":material/arrow_forward:"):
                st.session_state.selected_offer = offer["id"]
                st.rerun()


def details(offer):
    oid = offer["id"]
    if st.button("Wróć do listy", key="back", icon=":material/arrow_back:"):
        st.session_state.selected_offer = None
        st.rerun()
    st.title(offer["title"])
    st.caption(f'{offer["company"]} · {offer["location"]} · ogłoszenie fikcyjne')
    st.write(offer["salary"])
    selected = st.selectbox("Etap rekrutacji", STATUSES, index=STATUSES.index(offer["status"]), key=f"stage_{oid}")
    if selected != offer["status"]:
        offer["status"] = selected
        st.success("Status zapisany w tej sesji.")
    section = st.segmented_control("Widok oferty", ["Dopasowanie", "Dokumenty", "Notatki"], default="Dopasowanie", key=f"section_{oid}")
    if section == "Dokumenty":
        documents(offer)
    elif section == "Notatki":
        with st.form(f"notes_{oid}"):
            notes = st.text_area("Notatki do rekrutacji", value=offer["notes"], max_chars=2000, key=f"notes_text_{oid}")
            reminder = st.date_input("Data przypomnienia", value=offer["reminder"], key=f"reminder_{oid}")
            if st.form_submit_button("Zapisz notatki", type="primary"):
                offer.update(notes=notes, reminder=reminder)
                st.success("Notatki i data zostały zapisane w tej sesji.")
        st.caption("Data służy do planowania. Pokaz nie wysyła powiadomień.")
    else:
        st.subheader(f'Dopasowanie: {offer["score"]}/10')
        st.caption("Ocena przygotowana na potrzeby demonstracji; nie jest szansą zatrudnienia ani wynikiem bieżącego wywołania AI.")
        st.markdown("**Co pasuje**")
        for text in offer["strengths"]:
            st.write(f"✓ {text}")
        st.markdown("**Co sprawdzić**")
        for text in offer["gaps"]:
            st.write(f"• {text}")
        st.divider()
        st.subheader("Treść ogłoszenia")
        st.write(offer["text"])
        st.caption("Wynagrodzenia są fikcyjnymi kwotami brutto z ogłoszeń. Pokaz nie przelicza ich na netto.")


def documents(offer):
    oid = offer["id"]
    st.info("To gotowe przykłady dokumentów. Możesz je poprawić i pobrać; pokaz nie generuje nowej treści przez AI.")
    kind = st.selectbox("Rodzaj dokumentu", KINDS, key=f"kind_{oid}")
    versions = offer["documents"][kind]
    index = st.selectbox("Zapisana wersja", list(range(len(versions))), index=len(versions)-1,
                         format_func=lambda i: f'Wersja {i+1}' + (" · przykład" if i == 0 else " · korekta w sesji"),
                         key=f"version_{oid}_{kind}_{len(versions)}")
    content = versions[index]
    mode = st.segmented_control("Tryb dokumentu", ["Podgląd", "Edycja"], default="Podgląd", key=f"mode_{oid}_{kind}")
    if mode == "Edycja":
        with st.form(f"edit_{oid}_{kind}_{index}"):
            edited = st.text_area("Treść dokumentu", value=content, height=400, max_chars=20000,
                                  key=f"draft_{oid}_{kind}_{index}_{len(versions)}")
            if st.form_submit_button("Zapisz nową wersję", type="primary"):
                try:
                    if save_document(offer, kind, edited):
                        st.rerun()
                    else:
                        st.info("Treść jest taka sama jak w najnowszej wersji.")
                except ValueError as exc:
                    st.error(str(exc))
    else:
        with st.container(border=True):
            # User edits are plain text: do not render external images/HTML from input.
            st.text(dokumenty.content_to_send(content))
        if len(versions) > 1:
            st.caption(f"Zapisanych wersji: {len(versions)}. Możesz wrócić do wcześniejszej treści.")
        st.caption("Pobierasz wybraną, zapisaną wersję. Notatki dla użytkownika są pomijane w pliku.")
        with st.container(horizontal=True):
            st.download_button("Pobierz TXT", dokumenty.content_to_send(content).encode("utf-8"),
                               f"przyklad-{oid}.txt", "text/plain", key=f"txt_{oid}")
            st.download_button("Pobierz DOCX", lambda: eksport.to_docx(content, kind),
                               f"przyklad-{oid}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"docx_{oid}")
            st.download_button("Pobierz PDF", lambda: eksport.to_pdf(content, kind),
                               f"przyklad-{oid}.pdf", "application/pdf", key=f"pdf_{oid}")
        notes = dokumenty.split_document(content)["notatki"]
        if notes:
            with st.expander("Notatki do dokumentu — poza eksportem"):
                st.text(notes)
