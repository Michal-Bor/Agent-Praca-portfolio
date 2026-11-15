from pathlib import Path
import streamlit as st
st.title("Poradnik i budowa")
st.markdown((Path(__file__).resolve().parents[1] / "PORADNIK.md").read_text(encoding="utf-8"))
