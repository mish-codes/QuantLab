# Global Contagion Command Center — Phase 1 Design

**Date**: 2026-04-17
**Status**: design
**Author**: brainstormed with Claude

## Purpose

A Streamlit dashboard that visualises geopolitical risk contagion across a 3D globe, replaying two historical conflict periods frame-by-frame. Phase 1 ships the data pipeline, globe visualisation, and timeline playback. Gesture control (mediapipe + webrtc) is **explicitly Phase 2** and is not in scope here.

This is the flagship project for a new **Geopolitics & Risk** category in QuantLabs, with an accompanying methodology-focused blog post on FinBytes.

## Scope

### In
- ETL script that pulls raw prices from yfinance + FRED CSV endpoints for two conflict periods and writes a committed parquet file
- Streamlit page at `/Global_Contagion` with:
  - Period toggle (2020 US-Iran / 2024-2026 Hormuz)
  - Timeline slider + play/pause button (auto-advance ≈150ms/day)
  - pydeck `GlobeView` with 5 arcs from an aggregated Middle East origin to India / Turkey / Germany (contagion) and US / UK (safe haven)
  - Side panel: sparklines for Brent, Baltic Dry proxy, Gold, VIX with live correlation read-outs
- QuantLabs integration: new sidebar category, landing-page card, project registry entry
- Finance-methodology blog post on FinBytes

### Out (Phase 2+)
- Hand gesture control (mediapipe, streamlit-webrtc) — Phase 2
- Drill-in from aggregated origin to 3 component epicenter arcs on click — Phase 3
- Speed selector (1×/2×/4×), step buttons, key-event presets — Phase 3
- VIX-driven glow intensity — Phase 3
- Tech-demo blog post — Phase 2

## Architecture

```
scripts/fetch_contagion_data.py   (run manually)
        │
        ▼  writes
dashboard/data/contagion/events.parquet   (committed to repo)
        │
        ▼  read at page-load time
dashboard/pages/70_Global_Contagion.py    (Streamlit page)
        │
        ├─ pydeck GlobeView (arcs)        — main canvas
        ├─ st.slider + play button         — timeline control
        └─ st.columns side panel           — sparklines + correlations
```

### Data pipeline

**Script**: `scripts/fetch_contagion_data.py`
- Standalone, no Streamlit deps. Run manually; not on a schedule.
- Outputs: `dashboard/data/contagion/events.parquet`

**Tickers fetched**:

| Role | Source | Tickers |
|---|---|---|
| Epicenter (Middle East) | yfinance | `IGOV` proxy or individual ETFs; if bond yields unavailable for Israel/Saudi/UAE via yfinance, document fallback in the script |
| Contagion | yfinance + FRED CSV | India 10Y (`^INIRY` or FRED `IRLTLT01INM156N`), Turkey 10Y (FRED), Germany 10Y (FRED `IRLTLT01DEM156N`) |
| Safe haven | yfinance | `^TNX` (US 10Y), `GC=F` (Gold) |
| Energy link | yfinance | `BZ=F` (Brent), `BDRY` ETF as Baltic Dry proxy |
| Fear gauge | yfinance | `^VIX` |

**FRED access**: public CSV endpoints (e.g. `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10`). No API key. Wrapped in a helper that handles 429s with a sleep+retry.

**Date ranges (hardcoded)**:
- Period `2020_us_iran`: 2019-11-01 → 2020-03-15 (covers pre-escalation baseline + Soleimani strike + pre-COVID tail)
- Period `2024_hormuz`: 2024-01-01 → 2026-04-17 (today)

**Parquet schema** (raw prices only — correlations computed at runtime):

| column | dtype | notes |
|---|---|---|
| date | date | trading day |
| period | string | `2020_us_iran` or `2024_hormuz` |
| ticker | string | yfinance/FRED symbol |
| asset_role | string | `epicenter` / `contagion` / `safe_haven` / `energy` / `fear` |
| country | string | ISO-ish label for globe pinning (e.g. `DE`, `IN`, `TR`, `US`, `GB`); null for commodities/indices |
| close | float64 | closing price or yield |

Estimated size: ~15k rows × 6 cols ≈ <500 KB parquet. Safe for regular git.

### Streamlit page

**File**: `dashboard/pages/70_Global_Contagion.py`
**URL**: `/Global_Contagion`

**Layout** (wide):

```
[ QuantLabs sidebar ]   [ Main column                                    ]
                        [ Page header: "Global Contagion Command Center" ]
                        [ Period toggle (radio/segmented control)        ]
                        [ Globe (pydeck)                                 ]
                        [ Timeline slider + play/pause button            ]
                        [ Side panel: sparklines + correlation read-outs ]
```

**Controls**:
- `st.radio` or segmented control for period (two options)
- `st.slider` for date (range = period dates)
- `st.button("▶ Play")` that toggles to "⏸ Pause"; uses `st.session_state["playing"]` + `time.sleep` + `st.rerun()` loop for auto-advance
- Correlation window: hardcoded 7-day rolling (matches brief; tweak in code if needed)

**Globe viz** (pydeck `GlobeView`):
- Single origin node pinned at Strait of Hormuz (~26°N, 56°E), labelled "Middle East Risk Index" — **simple mean** of the 3 epicenter yields (day-by-day, after forward-filling weekends/holidays per-ticker). No z-scoring in Phase 1; keep the math transparent for the blog post.
- 5 destination nodes: Delhi (IN), Istanbul (TR), Frankfurt (DE), New York (US), London (GB)
- 5 `ArcLayer` entries; height ramps with `|correlation|`, thickness fixed for MVP
- **Color map**: diverging — red at +1 (contagion), gray at 0, green at −1 (decoupling / inverse). Implemented with a linear interpolation between `[0, 128, 0]` → `[128, 128, 128]` → `[200, 0, 0]` based on correlation value clipped to `[-1, 1]`.
- Dark globe base map to match the QuantLabs-neon-on-dark aesthetic hinted at in the brief

**Side panel** (under globe, `st.columns(4)`):
- Brent Crude sparkline + 7-day correlation to epicenter
- Baltic Dry proxy sparkline + correlation
- Gold sparkline + correlation (inverse-signal highlight)
- VIX sparkline + current level

### QuantLabs integration

1. **New category** `Geopolitics & Risk` added to `dashboard/lib/projects.py` registry
2. **New project entry** with:
   - `label`: "Global Contagion"
   - `description`: "Replay geopolitical shocks across a 3D globe — bond-yield contagion from Middle East to world markets"
   - `tech`: `["Python", "Streamlit", "pydeck", "pandas", "yfinance"]`
   - `page_link`: `"pages/70_Global_Contagion.py"`
3. **Landing-page card** auto-renders from the registry (same `_cat_card_html` used by existing projects — no new UI code needed)
4. **Sidebar entry** auto-renders from the registry (same pattern)

### Blog post (FinBytes)

- **Angle**: finance methodology — "Measuring Sovereign Contagion with Rolling Correlations"
- **Scope**: why bond yields proxy for CDS, what 7-day rolling correlation measures, how to interpret the 2020 US-Iran shock vs the 2024-2026 Hormuz tensions
- **Location**: `docs/_posts/` on the FinBytes repo
- **Cross-link**: links to the live QuantLabs page at `quantlabs.streamlit.app/Global_Contagion`
- **Writing**: done after the Streamlit page ships and we have screenshots to embed

## File structure (new/modified)

```
quant_lab/
├── scripts/
│   └── fetch_contagion_data.py           (new)
└── dashboard/
    ├── data/
    │   └── contagion/
    │       ├── events.parquet            (new, committed)
    │       └── README.md                 (new, how to re-run ETL)
    ├── lib/
    │   ├── contagion/                    (new package)
    │   │   ├── __init__.py
    │   │   ├── loader.py                 (load parquet, cache)
    │   │   ├── correlations.py           (rolling corr compute)
    │   │   └── globe.py                  (pydeck layer builders)
    │   └── projects.py                   (add Geopolitics & Risk category)
    ├── pages/
    │   └── 70_Global_Contagion.py        (new Streamlit page)
    └── tests/
        └── test_global_contagion.py      (new smoke tests)

finbytes_git/
└── docs/
    └── _posts/
        └── 2026-MM-DD-sovereign-contagion-rolling-correlations.html   (new, after Streamlit ships)
```

## Testing (Phase 1)

- `test_loads_without_error` — page imports and renders
- `test_shows_title` — title string present (matches existing test pattern)
- `test_period_toggle_switches_data` — flipping the period radio changes the underlying DataFrame row count
- `test_correlations_in_bounds` — every computed correlation is in `[-1, 1]`
- Unit tests for `correlations.py` rolling-corr helper with a synthetic series

## Risks / open questions (Phase 1)

1. **pydeck `GlobeView` is experimental** — if it breaks during development, fallback is streamlit-echarts with ECharts GL globe (option B from Q1). Budget: 1 day of pydeck wrestling before pivoting.
2. **FRED CSV rate limits** — daily caching via `st.cache_data` should prevent hitting limits, but the ETL script (run ad-hoc by humans) needs a retry-with-backoff helper.
3. **Bond yield data for Israel/Saudi/UAE via yfinance is patchy** — if specific tickers aren't available, the ETL script should log what it substituted and the blog post should acknowledge the proxy. Documented in `data/contagion/README.md`.
4. **Play button + Streamlit rerun loop** — `st.rerun()` in a sleep-loop is the conventional pattern but can feel janky. If frame rate is bad, fall back to a `st.empty()` container that only re-renders the globe layer, not the whole page.
5. **Parquet in git** — confirmed small (<500 KB), no LFS needed. But anchoring this here so we notice if the dataset grows 10×.

## Out of scope

These belong to Phase 2 / Phase 3 and will have their own specs:

- Webcam stream via streamlit-webrtc
- mediapipe hand landmark detection
- Gesture → globe transform mapping (rotate/pinch/swipe)
- Drill-in from aggregated epicenter to 3 component arcs
- Speed selector, step-forward/back, key-event preset buttons ("Soleimani strike", "Port attack")
- VIX-driven arc glow intensity
- Top-3 At-Risk markets overlay
- Tech-demo blog post
