"""Global Contagion Command Center — replays geopolitical shocks on a 3D globe.

Phase 1: data + globe + timeline. Gesture control ships in Phase 2.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

from contagion import constants, loader  # noqa: E402
from nav import render_sidebar  # noqa: E402
from page_header import render_page_header  # noqa: E402


st.set_page_config(
    page_title="Global Contagion — QuantLabs",
    page_icon="assets/logo.png",
    layout="wide",
)

render_sidebar()
render_page_header(
    "Global Contagion Command Center",
    "Visualising geopolitical-risk contagion on a 3D globe",
)


# ──────────────────────────────────────────────────────────────
# Project intro — what this is, what it tracks, how to read it
# ──────────────────────────────────────────────────────────────
with st.expander("ℹ️ About this project — what it shows & which tickers", expanded=False):
    st.markdown(
        """
        ### What this is

        A replay tool for two geopolitical episodes that rattled global markets:
        the **January 2020 US–Iran escalation** and the **2024–2026 Strait of
        Hormuz tensions**. For each episode we fetch daily prices for a curated
        set of tickers, compute a rolling correlation between a Middle-East
        "risk index" and major world markets, and draw those correlations as
        arcs on a 3D globe so you can *see* which markets caught contagion and
        which held up.

        Drag the slider (or press **▶ Play**) to watch the correlation field
        evolve day by day. Red arcs mean a market started moving *with* the
        Middle East (contagion); green arcs mean it moved *against* (classic
        flight-to-safety behaviour); gray means no relationship.

        ### Tickers considered

        | Role | Ticker(s) | Rationale |
        |---|---|---|
        | **Epicenter — Middle East risk** | `EIS`, `KSA`, `UAE` (iShares MSCI ETFs) | Bond-yield series for Israel / Saudi Arabia / UAE are not cleanly available via free data; sovereign-equity ETFs proxy the same risk premium. Their daily mean forms the **Middle East Risk Index**. |
        | **Contagion — energy-dependent economies** | `FRED:INDIRLTLT01STM` (India 10Y), `TUR` ETF (Turkey — FRED yield series discontinued), `FRED:IRLTLT01DEM156N` (Germany 10Y) | Large net importers whose sovereign risk tends to rise when oil supply is threatened. |
        | **Safe havens** | `^TNX` (US 10Y Treasury yield), `GC=F` (Gold futures) | Canonical crisis hedges — yields fall / gold rises when capital flees risk. |
        | **Energy link** | `BZ=F` (Brent Crude front month), `BDRY` ETF (Baltic Dry shipping proxy) | Direct transmission mechanism from Middle East supply shocks to global inflation / logistics. |
        | **Fear gauge** | `^VIX` | S&P 500 implied volatility — the market's thermometer for stress episodes. |

        Data fetched via `yfinance` and public FRED CSV endpoints, snapshotted
        into a committed parquet (`dashboard/data/contagion/events.parquet`)
        so the page has zero network dependencies at run time. Regenerate with
        `python scripts/fetch_contagion_data.py`.

        ### What's next

        **Phase 2** (designed, not yet shipped): hand-gesture control via
        `mediapipe` + `streamlit-webrtc` — pinch-zoom the globe, wave-rotate,
        two-finger-scrub the timeline. See
        `docs/superpowers/specs/2026-04-17-global-contagion-phase2-design.md`.
        """
    )


@st.cache_data(ttl=60 * 60 * 24)
def _load(period: str) -> pd.DataFrame:
    return loader.load_events(period=period)


# ──────────────────────────────────────────────────────────────
# Period toggle
# ──────────────────────────────────────────────────────────────
period_labels = {k: v["label"] for k, v in constants.PERIODS.items()}
period_key = st.radio(
    "Conflict period",
    options=list(period_labels.keys()),
    format_func=lambda k: period_labels[k],
    horizontal=True,
)

events = _load(period_key)

# ──────────────────────────────────────────────────────────────
# Timeline slider + play button
# ──────────────────────────────────────────────────────────────
dates = sorted(events["date"].unique())
if not dates:
    st.warning("No data for this period.")
    st.stop()

# Session state for playback + current cursor.
if "contagion_date_idx" not in st.session_state:
    st.session_state.contagion_date_idx = len(dates) - 1
if "contagion_playing" not in st.session_state:
    st.session_state.contagion_playing = False

# Clamp the cursor to the current period's range (period toggle may
# have shrunk `dates`).
if st.session_state.contagion_date_idx >= len(dates):
    st.session_state.contagion_date_idx = len(dates) - 1

col_slider, col_btn = st.columns([6, 1])
with col_slider:
    idx = st.slider(
        "Date",
        min_value=0,
        max_value=len(dates) - 1,
        value=st.session_state.contagion_date_idx,
        format="%d",
        label_visibility="collapsed",
    )
    st.session_state.contagion_date_idx = idx
with col_btn:
    btn_label = "⏸ Pause" if st.session_state.contagion_playing else "▶ Play"
    if st.button(btn_label, use_container_width=True):
        st.session_state.contagion_playing = not st.session_state.contagion_playing
        st.rerun()

selected_date = dates[st.session_state.contagion_date_idx]
st.caption(f"Showing snapshot at **{selected_date}**")

# Auto-advance while playing
if st.session_state.contagion_playing:
    import time as _time
    _time.sleep(0.15)
    if st.session_state.contagion_date_idx < len(dates) - 1:
        st.session_state.contagion_date_idx += 1
    else:
        st.session_state.contagion_playing = False   # stop at the end
    st.rerun()

# ──────────────────────────────────────────────────────────────
# Globe — pydeck ArcLayer on GlobeView
# ──────────────────────────────────────────────────────────────
import pydeck as pdk  # noqa: E402

from contagion import correlations, globe  # noqa: E402


def _correlations_for_date(events: pd.DataFrame, target_date) -> dict:
    """For each destination country, compute rolling-corr(ME index, country_yield)
    and return the value at `target_date`."""
    me_idx = correlations.middle_east_index(events)
    out: dict = {}
    for country, meta in constants.DESTINATION_CITIES.items():
        ticker = meta["ticker"]
        country_series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if country_series.empty:
            out[country] = 0.0
            continue
        # Align on common dates
        aligned = pd.concat([me_idx, country_series], axis=1, join="inner").dropna()
        if len(aligned) < constants.CORRELATION_WINDOW:
            out[country] = 0.0
            continue
        corr = correlations.rolling_corr(
            aligned.iloc[:, 0], aligned.iloc[:, 1],
            window=constants.CORRELATION_WINDOW,
        )
        # Pick the correlation at target_date (or most recent ≤ target_date)
        corr = corr.dropna()
        td = pd.Timestamp(target_date).date()
        mask = corr.index <= td
        out[country] = float(corr[mask].iloc[-1]) if mask.any() else 0.0
    return out


corr_by_country = _correlations_for_date(events, selected_date)
arc_rows = globe.build_arc_rows(corr_by_country)

# pydeck GlobeView with map_provider=None renders only layers we explicitly
# add. Without a basemap we'd see arcs floating in empty 3D space, so put a
# country-outline GeoJsonLayer behind the arcs. Natural Earth public URL.
_WORLD_COUNTRIES_URL = (
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/"
    "ne_50m_admin_0_scale_rank.geojson"
)

countries_layer = pdk.Layer(
    "GeoJsonLayer",
    data=_WORLD_COUNTRIES_URL,
    stroked=False,
    filled=True,
    get_fill_color=[40, 50, 70, 220],   # dark slate — matches the dashboard theme
    get_line_color=[80, 95, 115, 120],
    pickable=False,
)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arc_rows,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width=3,
    great_circle=True,
    pickable=True,
)

# zoom=0 gives the classic "full earth as a sphere in space" look on
# pydeck's GlobeView. Higher values flatten the curvature because the
# viewport fills with land before the sphere edge is visible.
view_state = pdk.ViewState(
    longitude=constants.EPICENTER_LONLAT[0],
    latitude=constants.EPICENTER_LONLAT[1],
    zoom=0,
    pitch=0,
    bearing=0,
)

deck = pdk.Deck(
    layers=[countries_layer, arc_layer],   # basemap first so arcs draw on top
    initial_view_state=view_state,
    views=[pdk.View(type="GlobeView", controller=True)],
    map_provider=None,   # GlobeView does not use tile maps
    tooltip={"text": "{dest_label}\nCorrelation: {correlation}"},
)

st.pydeck_chart(deck, use_container_width=True)

# Correlation read-out table under the globe
st.caption("Rolling 7-day correlation vs Middle East Risk Index")
st.dataframe(
    pd.DataFrame(
        [
            {"Country": constants.DESTINATION_CITIES[c]["label"], "Correlation": round(v, 3)}
            for c, v in corr_by_country.items()
        ]
    ),
    hide_index=True,
    use_container_width=True,
)


# ──────────────────────────────────────────────────────────────
# Methodology + safe haven write-up (collapsible)
# ──────────────────────────────────────────────────────────────
def _safe_haven_summary(events: pd.DataFrame) -> str:
    """Compute a short narrative on how the safe havens moved during the
    selected period. Returns markdown text."""
    me_idx = correlations.middle_east_index(events)

    def _window_corr(ticker: str) -> float | None:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if series.empty:
            return None
        aligned = pd.concat([me_idx, series], axis=1, join="inner").dropna()
        if len(aligned) < constants.CORRELATION_WINDOW:
            return None
        corr = correlations.rolling_corr(
            aligned.iloc[:, 0], aligned.iloc[:, 1],
            window=constants.CORRELATION_WINDOW,
        )
        return float(corr.dropna().mean()) if not corr.dropna().empty else None

    def _range_change(ticker: str) -> tuple[float, float] | None:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        if series.empty:
            return None
        return float(series.iloc[0]), float(series.iloc[-1])

    lines: list[str] = []
    for ticker, label in (("^TNX", "US 10Y Treasury yield"), ("GC=F", "Gold")):
        corr = _window_corr(ticker)
        rng = _range_change(ticker)
        if corr is None or rng is None:
            continue
        start, end = rng
        pct = ((end - start) / start * 100) if start else 0.0
        direction = "rose" if pct > 0 else "fell"
        interpret = (
            "tracked the Middle East index closely — limited safe-haven premium"
            if corr > 0.3
            else (
                "decoupled from the Middle East index — classic flight-to-safety signature"
                if corr < -0.3
                else "moved roughly independently of the Middle East index"
            )
        )
        lines.append(
            f"- **{label}** {direction} **{abs(pct):.1f}%** across the window "
            f"(avg 7-day corr to ME index: `{corr:+.2f}`) — {interpret}."
        )
    return "\n".join(lines) if lines else "_No safe-haven data for this period._"


with st.expander(
    "📘 How this works — correlation, safe havens, and how they responded",
    expanded=False,
):
    st.markdown(
        """
        #### How correlation is calculated

        Every ticker in the snapshot has a daily closing series for the selected
        period. The **Middle East Risk Index** is the simple mean of the three
        regional proxies (`EIS`, `KSA`, `UAE` ETF closes).

        For each destination country (Mumbai, Istanbul, Frankfurt, New York, London)
        we compute a **7-day rolling Pearson correlation** between the ME index
        and that country's 10-year yield (or ETF proxy where the yield series
        isn't publicly available). The timeline slider picks a date; the globe's
        arcs colour to the correlation value on that day.

        Reading the colours:
        - 🔴 **Red (+1)** — markets moved in lockstep with the Middle East: **strong contagion**.
        - ⚪ **Gray (0)** — no statistical relationship: markets decoupled or noise-dominated.
        - 🟢 **Green (−1)** — markets moved *against* the Middle East: **flight-to-safety or inverse hedging**.

        #### What counts as a "safe haven"

        Two assets are treated as reference safe havens:
        - **US 10-year Treasury yield (`^TNX`)** — when investors flee risk they buy
          US Treasuries, pushing yields down. A falling `^TNX` during a crisis
          episode is the classic flight-to-safety signature.
        - **Gold (`GC=F`)** — no counterparty risk, uncorrelated with equity cycles,
          tends to rally on geopolitical stress.

        The 🟢 arcs to **New York** and **London** on the globe capture the safe-haven
        hypothesis: when they go green during a Middle East risk spike, capital is
        flowing *away* from ME assets *toward* Treasuries and the GBP financial hub.
        """
    )
    st.markdown("#### How did they respond in this window?")
    st.markdown(_safe_haven_summary(events))


# ──────────────────────────────────────────────────────────────
# Side panel: Brent / Baltic / Gold / VIX sparklines
# ──────────────────────────────────────────────────────────────
st.markdown("### Energy, Safe Haven & Fear")

panel_tickers = [
    ("BZ=F", "Brent Crude"),
    ("BDRY", "Baltic Dry (ETF)"),
    ("GC=F", "Gold"),
    ("^VIX", "VIX"),
]
cols = st.columns(4)
for (ticker, label), col in zip(panel_tickers, cols):
    with col:
        series = (
            events[events["ticker"] == ticker]
            .set_index("date")["close"]
            .sort_index()
        )
        st.markdown(f"**{label}**")
        if series.empty:
            st.caption("no data")
            continue
        # Truncate to dates ≤ selected_date so the sparkline "plays along"
        series = series[series.index <= selected_date]
        st.line_chart(series, height=80)
        st.caption(f"Latest: {series.iloc[-1]:.2f}")
