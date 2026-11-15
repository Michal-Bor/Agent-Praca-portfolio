import streamlit as st
from portfolio_data import PROFILE, EXPECTATIONS
st.title("Profil przykładowy")
st.info("Anna Nowak jest fikcyjną kandydatką. Ten profil nie zawiera danych autora projektu.")
st.markdown(PROFILE)
st.subheader("Oczekiwania")
st.write(EXPECTATIONS)
st.caption("W pełnej wersji profil można edytować i potwierdzać przed użyciem przez AI. W pokazie pozostaje stały, aby oceny przykładowe miały ten sam punkt odniesienia.")
