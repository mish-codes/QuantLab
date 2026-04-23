"""Standard page initialisation for QuantLabs dashboard pages."""
import streamlit as st
from nav import render_sidebar
from page_header import render_page_header


def setup_page(title: str, subtitle: str) -> tuple:
    """Initialise a standard page. Returns (tab_app, tab_tests)."""
    render_sidebar()
    st.set_page_config(page_title=title, page_icon="assets/logo.png", layout="wide")
    render_page_header(title, subtitle)
    return st.tabs(["App", "Tests"])
