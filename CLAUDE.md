# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Multi-project quant-finance monorepo. The main shipped thing is a Streamlit multipage app under `dashboard/` deployed to **https://quantlabs.streamlit.app/**. Sibling repo **FinBytes** (`../finbytes_git/`) hosts the public blog at https://mish-codes.github.io/FinBytes/ and links into QuantLab pages as live demos.

Three parallel trees under the root:
- `dashboard/` — Streamlit app (main focus of most work).
- `projects/stock-risk-scanner/` — FastAPI + SQLAlchemy backend deployed to Render, consumed by one dashboard page.
- `exercises/` — self-contained teaching notebooks/folders, each with its own setup (pytest, pydantic, FastAPI, asyncio, yfinance, Claude API, docker, postgres). Never cross-import between exercises.

## Commands

### Dashboard local dev
```bash
cd dashboard && streamlit run app.py
```
`app.py` is deliberately thin — it just renders `static/resume.html` as the root so visitors land on the CV. The project hub is `pages/0_QuantLabs.py`. Override the `ENTER QUANTLABS →` target for local dev with `QUANTLABS_URL=http://localhost:8501/QuantLabs`.

### Dashboard tests
```bash
cd dashboard && pytest tests/ -q
```
**Must run from `dashboard/` cwd** — page-level tests use `AppTest.from_file("pages/NN_*.py")` with a relative path and will error with "File not found" if run from repo root.

Run a single test:
```bash
cd dashboard && pytest tests/test_global_contagion.py -q
```

### Backend (stock-risk-scanner)
```bash
cd projects/stock-risk-scanner && pip install -e ".[dev]" && pytest -v
```

### Data ETL
Committed parquets under `dashboard/data/` power the demos so runtime has zero network dependency. Regenerate via scripts:
```bash
python scripts/fetch_contagion_data.py      # Global Contagion → data/contagion/events.parquet
python scripts/build_london_ppd.py          # London house prices
```

### Deploy
- **Dashboard**: Streamlit Cloud auto-deploys `master`. No manual step. ~60-second lag after push.
- **Backend**: Render auto-deploys `master` for `projects/stock-risk-scanner/`. Free Postgres expires every 30 days — see `docs/MAINTENANCE.md` for the recreate flow (Churros admin page has a one-click button).

## Dashboard architecture

### Multipage layout
Streamlit's native page autodiscovery on `dashboard/pages/NN_*.py`. Numeric prefixes control sidebar order. `0_QuantLabs.py` is the hub (card grid of all projects). `99_Churros.py` is the admin page (gated by passphrase) — **excluded from the project registry on purpose so it doesn't appear on the public landing.**

### Shared lib (`dashboard/lib/`)
- `nav.py` — sidebar renderer imported by every page. Adds global CSS (`_GLOBAL_STYLES`) and silences noisy Streamlit deprecation warnings about `use_container_width` + `st.components.v1.html` since the Cloud version and local version can't agree on the replacement API.
- `projects.py` — single source of truth for the landing grid. `PROJECTS_BY_CATEGORY` (categorised) + `FEATURED_KEYS` (featured carousel order). Editing this file is how you add a project to the hub.
- `page_header.py`, `charts.py`, `plotting.py`, `risk_colors.py` — shared UI primitives.
- Per-feature submodules — `contagion/`, `rentbuy/`, `benchmark/`, `bigo/`, `house_prices.py`, `finance.py`, `api_client.py`, `mermaid.py`. Kept small and composable; pages import from these, not from each other.

### Page idiom
Pages almost always begin with:
```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from nav import render_sidebar
render_sidebar()
```
The `parents[1]` is correct — pages live in `dashboard/pages/`, so `parents[1]` is `dashboard/`. A few older pages had `.parent` instead and crashed on Cloud — watch for this when adding new pages.

### Streamlit Cloud gotchas that bit us
- **`st.pydeck_chart` silently ignores `views=` config** → always use `components.html(deck.to_html(as_string=True))` when you need a non-default view (e.g. globe).
- **`pdk.View(type="GlobeView")` silently falls back to flat map** → the canonical class is `_GlobeView` (leading underscore).
- **pydeck 0.9.1 prefixes BitmapLayer `image` with `@@=`** (treats data URL as accessor expression). Regex-strip after `deck.to_html()`: `re.sub(r'"image"\s*:\s*"@@=', '"image": "', html)`.
- **Cloud doesn't statically serve `dashboard/assets/**`.** Bundle + base64 for small assets, or use jsDelivr (`cdn.jsdelivr.net/gh/<user>/<repo>@<branch>/path`) for large ones so the browser can cache them.
- **`st.dataframe(df.style.map(...))` silently drops cell backgrounds** on some pandas/Cloud combos. Use hand-rolled HTML tables with inline `style=` for guaranteed cell colouring.
- **`st.rerun()` halts the script immediately.** Any animation-loop `if playing: sleep, advance, st.rerun()` block must be the **last** code in the page — anything below it doesn't render during playback.
- **Vega-embed components (`st.altair_chart`) are throttled** during rapid `st.rerun()` loops. For smooth frame-by-frame animation use inline SVG via `st.markdown(unsafe_allow_html=True)`.

More detail on all of these in the personal auto-memory file `feedback_streamlit_rerun_gotchas.md`.

## Data conventions

- Committed parquets under `dashboard/data/<feature>/*.parquet` — each page loads via an `@st.cache_data` loader in its feature module. Runtime does zero network I/O.
- Natural Earth GeoJSON bundled at `dashboard/assets/geojson/world_countries.geojson` (Cloud can't reliably fetch from remote CDNs without HTML error responses).
- Monthly FRED series (e.g. India 10Y yield) use a 3-month rolling correlation window; daily tickers use the 7-day window. Mixing monthly + daily and forward-filling produces zero-variance stretches → `±inf` correlations, so defend with `.replace([inf,-inf], nan).dropna()` after any rolling-corr.

## Git workflow

Work on `working`, merge directly to `master`. A global pre-commit hook at `~/.git-hooks/` blocks direct commits to `master` but **not merges** — use `--no-verify` on the merge step to bypass the hook.

```bash
git checkout working
# hack hack
git add <files>
git commit -m "<message>"
git push origin working
git checkout master
git merge working --no-verify -m "<message>"
git push origin master
git checkout working    # always end on working
```

Streamlit Cloud auto-deploys ~60 seconds after `master` is pushed.

**Don't push follow-up commits to `working` while a PR is open** (if using the GitHub PR flow) — squash-merge strands anything pushed after the merge point and forces a new PR.

## CI

`.github/workflows/test.yml` runs on push + PR to `master`:
- **Backend Tests** — pytest in `projects/stock-risk-scanner/`.
- **Dashboard Tests** — pytest in `dashboard/` with a stub `.streamlit/secrets.toml`. All `AppTest.from_file(...)` calls assume the cwd is `dashboard/` (same as the local test command).

## Repo layout quick map

```
dashboard/          Streamlit app → quantlabs.streamlit.app
  app.py            Resume landing (thin)
  pages/            0_QuantLabs hub, NN_<feature>.py per page, 99_Churros admin
  lib/              Shared UI + per-feature logic (nav, projects, contagion/, rentbuy/, ...)
  data/             Committed parquets (ETL output, not runtime-fetched)
  assets/           Logo, night-lights JPG, bundled GeoJSON
  static/           resume.html served at "/" via components.html
  tests/            pytest — run from this dir
  scripts/          (small dashboard-local scripts)

projects/
  stock-risk-scanner/   FastAPI + async SQLAlchemy backend, Render-deployed

exercises/          01-pytest-tdd .. 08-postgres-sqlalchemy, each self-contained

scripts/            Repo-level ETL + ops (fetch_contagion_data, build_london_ppd, rds)

docs/               MAINTENANCE.md (Render 30-day DB rotation), aws/github-oidc setup,
                    superpowers/ (specs + plans for in-flight features)
```
