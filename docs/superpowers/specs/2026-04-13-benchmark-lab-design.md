# Benchmark Lab — Pandas vs Polars (DRAFT / WIP)

**Status:** Brainstorming in progress — paused 2026-04-13. Resume by continuing the brainstorming skill flow with the open questions at the bottom.

## Project framing

A Streamlit-hosted "benchmark lab" that runs a fixed set of dataframe operations in both pandas and polars, side-by-side, on user-supplied data. The primary goal is **"build at home, reuse at work"** — the tool must be local-first, work on arbitrary CSV/Parquet files, and not depend on cloud services.

The user has already published [pandas-vs-polars blog post](../../../_posts/2026-07-08-pandas-vs-polars.html) in FinBytes but has not shipped polars in code anywhere. This project closes that loop with an empirical demonstration.

## Locked-in decisions

| Area | Decision |
|---|---|
| **Project identity** | Benchmark lab — pandas vs polars comparison |
| **Location** | New Streamlit page `dashboard/pages/43_Benchmark_Lab.py` in QuantLab |
| **Project shape** | **Option C: one-click benchmark suite** (not interactive exploration, not engine-toggle) |
| **Primary dataset** | **TfL Santander Cycle Hire** (CSV via URL fetch with preset dropdown) |
| **Scope** | Generic benchmark on any tabular file — cycle hire is the showcase dataset, not the only supported one |
| **Operations (7 fixed)** | 1. Read CSV · 2. Count rows · 3. Filter · 4. Groupby + aggregate · 5. Sort · 6. String extract (regex) · 7. Write Parquet |
| **Column configuration** | Auto-detect sensible defaults (first string, first numeric, first timestamp) with user override via dropdowns |
| **Metrics** | Wall time + peak memory + rows/sec throughput |
| **Methodology** | Median of 3 runs with 1 discarded warmup run. For `Read CSV` specifically, show cold vs warm separately. |
| **Output** | Results table + bar charts + CSV/markdown export + correctness indicator (hash check both engines return same answer) |
| **File ingestion** | URL fetch server-side (not `st.file_uploader`). Preset dropdown + custom URL input. |

## Architecture outline (Section 1 of the design — APPROVED)

```
dashboard/lib/benchmark/
  __init__.py
  engines.py        # pandas + polars implementations of each of the 7 ops (pure fns, no timing)
  runner.py         # orchestration: warmup, N runs, memory sampling, error capture per op
  datasets.py       # TfL preset URLs, download helper with caching, column auto-detect
  report.py         # results -> DataFrame/charts/markdown export
  showcases.py      # (stretch) dataset-specific AnalysisQuestion presets

dashboard/pages/43_Benchmark_Lab.py   # UI glue only, no logic
```

### Module responsibilities

**`engines.py`** — pure functions per operation, one pandas variant and one polars variant. No timing/measurement.

**`runner.py`** — `run_benchmark(path, ops, column_config) -> list[OpResult]`. `OpResult` carries wall_ms median + all runs, peak_mb, rows_processed, rows_per_sec, error, result_hash.

**`datasets.py`** — `TFL_PRESETS` dict of known URLs, `download(url, cache_dir)` with progress and local cache, `auto_detect_columns(df)` for sensible defaults.

**`report.py`** — converts results list into Streamlit-friendly outputs: pandas DataFrame for `st.dataframe`, Plotly figures for comparison charts, markdown string for copy/export.

**`showcases.py`** (proposed, not yet approved) — dataset-specific question presets:
```python
@dataclass
class AnalysisQuestion:
    key: str
    label: str
    description: str
    pandas_fn: Callable     # (df) -> (result_df, answer_text)
    polars_fn: Callable
    dataset_key: str        # "tfl_cycles" - which schema this works on
```

### Why this split
- **Testable** — engines.py and runner.py are plain Python, pytest-able without Streamlit's test harness
- **Portable** — benchmark engine is separable from UI; at work, could be imported into Jupyter or a CLI script
- **Follows existing pattern** — matches `dashboard/lib/render_admin.py`, `house_prices.py`, `test_tab.py` conventions

## Open questions (resume here)

These were raised but not yet answered. When resuming, ask them one at a time per the brainstorming skill flow:

### 1. Analysis mode (preset questions) — in MVP or stretch?

The idea: alongside the 7 generic benchmark operations, add a dropdown of **pre-baked analysis questions** ("Top 10 busiest stations", "Average duration by hour", etc.) that the tool answers using both engines, showing the real answer + timing comparison. Proposed ~5-6 questions for MVP:

1. Top 10 busiest start stations by trip count
2. Average trip duration by hour of day
3. Most popular station pair (source → destination)
4. Longest single trip
5. Trip volume by weekday
6. Median trip duration per start station (top 20)

Sub-questions:
- **Q1a**: Include in MVP, or stretch feature after the generic benchmark ships?
- **Q1b**: If included, 3 / 5–6 / 10 questions?
- **Q1c**: Tabs (Benchmark tab + Analysis tab) or toggle on a single view?

### 2. Streamlit Cloud resource limits — guardrail strategy

Streamlit Cloud free tier: ~1 GB RAM, ~1 GB ephemeral disk, shared CPU. Big files will OOM the container.

Proposed guardrails:
1. **Bundled sample** committed to the repo (~20 MB, 1 week of TfL data) so demo always works
2. **Environment-aware file size cap** — detect cloud, cap at ~150 MB; local, no cap (or 10 GB)
3. **Content-Length pre-check** before downloading, refuse with clear error if too large
4. **Preset dropdown filtered by environment** — cloud shows bundled + 1-2 small files; local shows everything
5. **`gc.collect()` between engines** to prevent pandas + polars memory stacking
6. **Prominent cloud banner** warning about the limit
7. **Disable heavy operations on cloud** (optional) — multi-GB sorts/groupbys skipped

Sub-questions:
- **Q2a**: 150 MB cloud cap — too tight, too loose, or right?
- **Q2b**: Bundled sample size — 20 MB (1 week) or 50 MB (1 month)?
- **Q2c**: Cloud banner prominence — top-of-page warning vs info expander?

### 3. Remaining design sections not yet covered (after open questions are resolved)

Per the brainstorming skill, still need to present and approve:
- Section 2: Data flow (user clicks → download → benchmark orchestration → results display)
- Section 3: UI layout / page structure
- Section 4: Error handling strategy
- Section 5: Testing strategy

After all five sections are approved, write the final (non-draft) design doc and invoke `superpowers:writing-plans` for the implementation plan.

## Context for resuming

- **Brainstorming skill flow**: the design must be presented in sections scaled to complexity, user approves each section, then write final design doc, then spec self-review, then user review, then transition to implementation via `writing-plans` skill.
- **Hard gate**: NO code, NO implementation skill invocation until the user has approved the final written design doc.
- **Conversation state**: user picked A (standalone new page in QuantLab), C (benchmark suite), C (table + charts + export), and accepted my recommendation for methodology (median of 3 + warmup, cold/warm split for CSV read). They paused because Q1 and Q2 above need thought.
