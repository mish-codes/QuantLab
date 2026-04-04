from pathlib import Path
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="System Health | FinBytes QuantLabs", page_icon="🩺", layout="wide")

st.title("System Health")
st.markdown("Live status of all services powering FinBytes QuantLabs.")

API_URL = st.secrets.get("API_URL", "http://localhost:8000")
GITHUB_REPO = "MishCodesFinBytes/QuantLab"


def check_api() -> dict:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=10)
        if resp.status_code == 200:
            return {"status": "ok", "detail": "API is responding"}
        return {"status": "error", "detail": f"HTTP {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "detail": "Cannot connect — backend may be sleeping (Render free tier wakes on first request)"}
    except requests.exceptions.Timeout:
        return {"status": "error", "detail": "Request timed out"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def check_db() -> dict:
    try:
        resp = requests.get(f"{API_URL}/api/health/db", timeout=10)
        data = resp.json()
        return data
    except requests.exceptions.ConnectionError:
        return {"status": "error", "database": "API offline — cannot check database"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


def get_ci_status() -> dict:
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs",
            params={"per_page": 5},
            timeout=10,
        )
        if resp.status_code != 200:
            return {"status": "unknown", "detail": "Could not fetch CI status"}
        runs = resp.json().get("workflow_runs", [])
        if not runs:
            return {"status": "unknown", "detail": "No CI runs found"}

        latest = runs[0]
        return {
            "status": "ok" if latest["conclusion"] == "success" else "error",
            "conclusion": latest.get("conclusion", "in_progress"),
            "name": latest["name"],
            "run_number": latest["run_number"],
            "url": latest["html_url"],
            "created_at": latest["created_at"][:10],
        }
    except Exception as e:
        return {"status": "unknown", "detail": str(e)}


# --- Run all checks ---
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

# API check
with col1:
    st.markdown("### API")
    api = check_api()
    if api["status"] == "ok":
        st.success("Online")
    else:
        st.error("Offline")
    st.caption(api.get("detail", ""))

# DB check
with col2:
    st.markdown("### Database")
    db = check_db()
    if db.get("status") == "ok":
        st.success("Connected")
    else:
        st.error("Disconnected")
    st.caption(db.get("database", db.get("detail", "")))

# CI check
with col3:
    st.markdown("### CI Pipeline")
    ci = get_ci_status()
    if ci["status"] == "ok":
        st.success(f"Passing (#{ci.get('run_number', '?')})")
    elif ci["status"] == "error":
        st.error(f"Failing (#{ci.get('run_number', '?')})")
    else:
        st.warning("Unknown")
    if "url" in ci:
        st.caption(f"[View run]({ci['url']}) — {ci.get('created_at', '')}")
    else:
        st.caption(ci.get("detail", ""))

# Dashboard check
with col4:
    st.markdown("### Dashboard")
    st.success("Running")
    st.caption("You're seeing this page")

# --- Test Results from CI ---
st.markdown("---")
st.markdown("## Latest Test Results")

st.markdown(
    f"![Tests](https://github.com/{GITHUB_REPO}/actions/workflows/test.yml/badge.svg)"
)

ci_data = get_ci_status()
if ci_data.get("url"):
    conclusion = ci_data.get("conclusion", "unknown")
    icon = "✅" if conclusion == "success" else "❌" if conclusion == "failure" else "⏳"
    st.markdown(
        f"**Last run:** {icon} [{ci_data['name']} #{ci_data['run_number']}]({ci_data['url']}) "
        f"— **{conclusion}** — {ci_data.get('created_at', '')}"
    )

st.markdown("### Test Suite (27 tests)")

# Individual test status from latest CI run
TESTS = [
    ("test_api.py", "TestHealthEndpoint", "test_health", "GET /health returns 200"),
    ("test_api.py", "TestHealthDb", "test_db_connected", "GET /api/health/db returns connected"),
    ("test_api.py", "TestCreateScan", "test_returns_pending", "POST /api/scan returns 202 + pending"),
    ("test_api.py", "TestGetScan", "test_returns_scan_by_id", "GET /api/scans/{id} returns scan"),
    ("test_api.py", "TestGetScan", "test_returns_404_for_missing_id", "GET /api/scans/9999 returns 404"),
    ("test_api.py", "TestListScans", "test_returns_list", "GET /api/scans returns list"),
    ("test_db_layer.py", "TestCreatePendingScan", "test_creates_pending_record", "Insert pending scan record"),
    ("test_db_layer.py", "TestCompleteScan", "test_updates_to_complete", "Update scan to complete with metrics"),
    ("test_db_layer.py", "TestFailScan", "test_updates_to_failed", "Update scan to failed with error"),
    ("test_db_layer.py", "TestGetScan", "test_returns_record_by_id", "Fetch scan by ID"),
    ("test_db_layer.py", "TestGetScan", "test_returns_none_for_missing_id", "Returns None for missing ID"),
    ("test_db_layer.py", "TestGetRecentScans", "test_returns_completed_scans_newest_first", "Recent scans ordered newest first"),
    ("test_market_data.py", "TestFetchPrices", "test_successful_fetch", "yfinance download returns DataFrame"),
    ("test_market_data.py", "TestFetchPrices", "test_empty_data_raises", "Empty data raises ValueError"),
    ("test_models.py", "TestScanRequest", "test_valid_request", "Valid request accepted"),
    ("test_models.py", "TestScanRequest", "test_tickers_uppercased", "Tickers auto-uppercased"),
    ("test_models.py", "TestScanRequest", "test_mismatched_lengths_raises", "Mismatched tickers/weights raises"),
    ("test_models.py", "TestScanRequest", "test_weights_not_summing_to_one_raises", "Bad weight sum raises"),
    ("test_models.py", "TestRiskMetrics", "test_risk_metrics_fields", "RiskMetrics stores all fields"),
    ("test_models.py", "TestScanResult", "test_scan_result_fields", "ScanResult stores all fields"),
    ("test_narrative.py", "TestRiskNarrator", "test_generate_with_api", "Claude API returns narrative"),
    ("test_narrative.py", "TestRiskNarrator", "test_generate_api_error_returns_fallback", "API error returns fallback"),
    ("test_narrative.py", "TestRiskNarrator", "test_generate_no_api_key_returns_fallback", "No API key returns fallback"),
    ("test_risk.py", "TestCalculateRiskMetrics", "test_var_and_cvar", "VaR negative, CVaR worse than VaR"),
    ("test_risk.py", "TestCalculateRiskMetrics", "test_max_drawdown", "Max drawdown calculation correct"),
    ("test_risk.py", "TestCalculateRiskMetrics", "test_sharpe_ratio_sign", "Sharpe positive for up, negative for down"),
    ("test_scanner.py", "TestScan", "test_full_pipeline", "Full pipeline: fetch → risk → narrative → result"),
]

ci_passing = ci_data.get("conclusion") == "success" if ci_data.get("status") != "unknown" else None

for file, cls, name, desc in TESTS:
    if ci_passing is True:
        st.markdown(f"✅ **{cls}::{name}** — {desc}")
    elif ci_passing is False:
        st.markdown(f"⚠️ **{cls}::{name}** — {desc} *(check CI for details)*")
    else:
        st.markdown(f"⬜ **{cls}::{name}** — {desc}")

# --- Service details ---
st.markdown("---")
st.markdown("## Service Details")

st.markdown(f"""
| Service | URL | Hosting | Notes |
|---------|-----|---------|-------|
| Dashboard | [finbytes.streamlit.app](https://finbytes.streamlit.app) | Streamlit Community Cloud | Free, auto-deploys from master |
| API | [finbytes-scanner.onrender.com]({API_URL}) | Render Free Tier | Sleeps after 15min idle |
| Database | Internal (Render) | Render PostgreSQL Free | **Expires 90 days after creation** |
| CI | [GitHub Actions](https://github.com/{GITHUB_REPO}/actions) | GitHub Free | 2000 mins/month |
| Blog | [FinBytes](https://mishcodesfinbytes.github.io/FinBytes/) | GitHub Pages | Free |
""")

st.warning(
    "**Render PostgreSQL free tier expires after 90 days.** "
    "If the Database check above shows red, recreate the database on Render "
    "and update the DATABASE_URL environment variable."
)
