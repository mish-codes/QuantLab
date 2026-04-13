"""Shared tech stack footer for project pages.

Renders a horizontal rule then a row of styled pill-shaped badges listing
the technologies used on the current page. Call at the bottom of every
project page:

    from tech_footer import render_tech_footer
    render_tech_footer(["Python", "Plotly", "Streamlit"])
"""

import streamlit as st

_BADGE_STYLE = (
    "display:inline-block;"
    "padding:3px 10px;"
    "margin:3px 4px 3px 0;"
    "background:rgba(42,122,226,0.10);"
    "color:#2a7ae2;"
    "border:1px solid rgba(42,122,226,0.30);"
    "border-radius:12px;"
    "font-size:0.78rem;"
    "font-weight:600;"
    "letter-spacing:0.02em;"
)

_LABEL_STYLE = (
    "display:block;"
    "font-size:0.72rem;"
    "font-weight:700;"
    "letter-spacing:0.08em;"
    "text-transform:uppercase;"
    "color:var(--text-muted-color,#888);"
    "margin-bottom:6px;"
)


def render_tech_footer(tech_list):
    """Render a styled tech-stack footer.

    Args:
        tech_list: list of tech names (strings) used on this page.
    """
    if not tech_list:
        return
    st.markdown("---")
    badges_html = "".join(
        f'<span style="{_BADGE_STYLE}">{t}</span>' for t in tech_list
    )
    st.markdown(
        f'<div style="margin-top:1rem;">'
        f'<span style="{_LABEL_STYLE}">Tech Stack</span>'
        f'{badges_html}'
        f'</div>',
        unsafe_allow_html=True,
    )
