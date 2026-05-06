"""INQLAB — generative art gallery embedded from inqlab.uk."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

import streamlit as st
import streamlit.components.v1 as components
from nav import render_sidebar
from page_header import render_page_header
from tech_footer import render_tech_footer

st.set_page_config(page_title="INQLAB", page_icon="assets/logo.png", layout="wide")
render_sidebar()
render_page_header("INQLAB", "Generative art — code & colour")

st.markdown(
    "19 generative art tools combining historical colour theory (Sanzo Wada, Werner, "
    "Kalamkari) with algorithmic composition. Each piece is unique, signed, and "
    "downloadable as a PNG. Use the arrows to browse, or click **Open →** to open a "
    "tool full-screen."
)

components.iframe(
    "https://www.inqlab.uk",
    height=820,
    scrolling=True,
)

render_tech_footer(["Canvas API", "WebGL", "vanilla JS", "GitHub Pages", "Streamlit components"])
