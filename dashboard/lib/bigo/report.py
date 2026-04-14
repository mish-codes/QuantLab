"""Report builders: Plotly log-log chart + per-variant card contents."""

from __future__ import annotations

import math

import plotly.graph_objects as go

from .runner import ProblemResult, VariantResult


# Color palette — distinguishable on log-log without being garish
_VARIANT_COLORS = [
    "#e24a4a",  # red
    "#2a7ae2",  # blue
    "#2ea043",  # green
    "#e8893c",  # orange
    "#a371f7",  # purple
    "#17becf",  # cyan
    "#bcbd22",  # olive
]


def _theoretical_curve(big_o: str, xs: list, anchor_x: float, anchor_y: float):
    """Compute a y-curve for the given Big O label, scaled to pass
    (approximately) through (anchor_x, anchor_y).

    Returns None if the label is not recognized.
    """
    label = big_o.replace(" ", "").lower()

    def base(x):
        if label in ("o(1)",):
            return 1.0
        if label in ("o(logn)",):
            return math.log2(max(x, 2))
        if label in ("o(n)",):
            return float(x)
        if label in ("o(nlogn)",):
            return x * math.log2(max(x, 2))
        if label in ("o(n^2)", "o(n²)"):
            return float(x) * x
        if label in ("o(2^n)", "o(2ⁿ)"):
            return float(2 ** x)
        return None

    anchor_base = base(anchor_x)
    if anchor_base is None or anchor_base == 0:
        return None
    scale = anchor_y / anchor_base
    ys = []
    for x in xs:
        b = base(x)
        if b is None:
            return None
        ys.append(b * scale)
    return ys


def build_complexity_chart(result: ProblemResult) -> go.Figure:
    """Build the log-log wall-time-vs-n chart for one ProblemResult."""
    fig = go.Figure()
    for idx, vr in enumerate(result.variant_results):
        color = _VARIANT_COLORS[idx % len(_VARIANT_COLORS)]
        # Empirical line — only non-error, non-skipped points
        xs = [p.n for p in vr.points if p.error is None and not p.skipped]
        ys = [p.wall_ms for p in vr.points if p.error is None and not p.skipped]
        if xs:
            fig.add_trace(go.Scatter(
                x=xs, y=ys,
                mode="lines+markers",
                name=f"{vr.variant.label}  {vr.variant.big_o}",
                line=dict(color=color, width=2),
                marker=dict(size=7),
            ))
            # Theoretical overlay, anchored to smallest point
            theory_ys = _theoretical_curve(vr.variant.big_o, xs, xs[0], ys[0])
            if theory_ys is not None:
                fig.add_trace(go.Scatter(
                    x=xs, y=theory_ys,
                    mode="lines",
                    name=f"{vr.variant.big_o} theoretical",
                    line=dict(color=color, width=1, dash="dash"),
                    opacity=0.4,
                    showlegend=False,
                ))

    fig.update_layout(
        title="Wall time per algorithm (log-log axes)",
        xaxis_title="n (input size)",
        yaxis_title="Wall time (ms)",
        xaxis=dict(type="log"),
        yaxis=dict(type="log"),
        height=450,
        margin=dict(t=60, b=40, l=50, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    return fig


def _row_status(point) -> str:
    if point.error is not None:
        return f"error: {point.error}"
    if point.skipped:
        return "skipped"
    return f"{point.wall_ms:.3f} ms"


def build_variant_card(vr: VariantResult) -> dict:
    """Build a dict the Streamlit UI renders inside an expander for one variant.

    Returns:
        {
          "headline": str,
          "rows": list[dict],
        }
    """
    successful = [p for p in vr.points if p.error is None and not p.skipped]
    if successful:
        last = successful[-1]
        headline_tail = f"n={last.n} in {last.wall_ms:.3f} ms"
    else:
        skipped = [p for p in vr.points if p.skipped]
        errored = [p for p in vr.points if p.error is not None]
        if skipped:
            headline_tail = "all skipped (over budget)"
        elif errored:
            headline_tail = f"errored: {errored[0].error}"
        else:
            headline_tail = "no data"

    headline = f"{vr.variant.label}  ·  {vr.variant.big_o}  ·  {headline_tail}"

    rows = [{"n": p.n, "status": _row_status(p)} for p in vr.points]
    return {"headline": headline, "rows": rows}
