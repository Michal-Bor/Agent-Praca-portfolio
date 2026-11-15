"""Public entrypoint: deliberately does not import agent/config/db or read .env."""
import streamlit as st
from portfolio_data import new_state

st.set_page_config(page_title="Agent Praca · portfolio", page_icon=":material/work:", layout="centered")
if "offers" not in st.session_state:
    st.session_state.offers = new_state()
    st.session_state.selected_offer = None

pages = st.navigation([
    st.Page("app_pages/oferty.py", title="Oferty", icon=":material/work:", default=True),
    st.Page("app_pages/aplikacje.py", title="Moje aplikacje", icon=":material/checklist:"),
    st.Page("app_pages/profil.py", title="Profil przykładowy", icon=":material/person:"),
    st.Page("app_pages/poradnik.py", title="Poradnik i budowa", icon=":material/help:"),
])
with st.sidebar:
    st.caption("PORTFOLIO · INTERAKTYWNY POKAZ")
    st.markdown("**Od oferty do przygotowanej aplikacji.**")
    st.caption("Fikcyjne dane. Bez wywołań AI i bez wysyłania aplikacji.")
    st.link_button("Kod na GitHub", "https://github.com/Michal-Bor/Agent-Praca-portfolio", icon=":material/code:")
    if st.button("Zresetuj pokaz", icon=":material/restart_alt:", key="reset"):
        for key in list(st.session_state):
            del st.session_state[key]
        st.rerun()
    st.caption("Zmiany są przechowywane w pamięci Twojej sesji. Mogą zniknąć po przeładowaniu strony. Używaj danych przykładowych.")

pages.run()
