"""Custom Streamlit component: a persistent deck.gl `_GlobeView`.

The built-in ``components.html(deck.to_html(...))`` pattern reloads the
iframe on every rerun — during the Global Contagion playback loop that
caused a visible strobe/flicker on every frame. This component mounts
deck.gl *once* inside the iframe; on each subsequent Streamlit rerun
only the new arc data (and correlation-driven destination fills)
travels over the websocket, and deck.gl's internal diff updates the
layer buffers in place without reloading the iframe.

Usage:
    from components.contagion_globe import contagion_globe
    contagion_globe(
        arcs=[...],
        destination_features={...},
        epicenter_features={...},
        night_lights_url="https://...",
        view_state={"longitude": 56, "latitude": 34, "zoom": 1,
                    "pitch": 35, "bearing": 0},
        colour_trigger=selected_date.isoformat(),
        height=980,
        key="globe",
    )

The ``colour_trigger`` argument is a cache-buster: pass the current
selected date (or any string that changes when arc colours change) so
deck.gl's ``updateTriggers`` map knows to re-evaluate the colour
accessors. Without this, deck.gl keeps stale colours because the
``data=`` array length didn't change.
"""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
_INDEX_HTML = _FRONTEND_DIR / "index.html"
_NIGHT_LIGHTS = _FRONTEND_DIR / "world_night.jpg"


@lru_cache(maxsize=1)
def _build_data_url() -> str:
    """Build a self-contained data: URL for the component frontend.

    Streamlit Cloud kept failing to load our component via both
    ``path=`` (Cloud serves the files) and ``url=<external CDN>``:
    iframes timed out with "trouble loading the component" before any
    postMessage could fire. The data: URL approach sidesteps Cloud's
    component-serving layer entirely — the iframe's ``src`` is the
    raw HTML inline, no external fetch. Image references inside the
    HTML get replaced with an inlined base64 data URL at build time
    so the iframe is fully self-contained.

    Size: roughly 1.1 MB of HTML + 1 MB of base64 image = ~1.4 MB
    data: URL. Well under Chromium's data-URL cap. Cached with
    lru_cache so the encoding happens once per Python process.
    """
    raw_html = _INDEX_HTML.read_text(encoding="utf-8")
    img_b64 = base64.b64encode(_NIGHT_LIGHTS.read_bytes()).decode("ascii")
    inline_img = f"data:image/jpeg;base64,{img_b64}"
    # Frontend defaults to './world_night.jpg'; replace that with the
    # inline data URL so the iframe doesn't try to resolve a relative
    # path (which has no base URL under a data: src).
    html_with_inline_image = raw_html.replace("./world_night.jpg", inline_img)
    encoded = base64.b64encode(html_with_inline_image.encode("utf-8")).decode("ascii")
    return f"data:text/html;base64,{encoded}"


# Register the component with a data: URL. Streamlit sets the iframe's
# src to this URL; the browser decodes and renders inline, no network
# request out to Streamlit Cloud's component endpoint or an external
# CDN. The component protocol (streamlit:componentReady +
# streamlit:render postMessages) works the same — postMessage with
# '*' target is cross-origin-safe, which data: URLs count as.
_component_func = components.declare_component(
    "contagion_globe",
    url=_build_data_url(),
)


def contagion_globe(
    *,
    arcs: list[dict],
    destination_features: dict,
    epicenter_features: dict,
    view_state: dict,
    colour_trigger: str,
    night_lights_url: str | None = None,
    height: int = 980,
    key: str | None = None,
):
    """Mount the persistent deck.gl globe component.

    Arc data, destination-country fill colours, and view state are
    passed every rerun. The frontend keeps the same Deck instance
    alive across renders and only updates the layers via setProps —
    no iframe reload, no WebGL re-init.

    ``night_lights_url`` is optional. If omitted, the frontend uses
    the JPG bundled alongside index.html inside the component
    directory (served by Streamlit from the same origin as the
    iframe — no CORS / no CDN fetch). Pass an explicit URL only if
    you want a different globe texture.
    """
    return _component_func(
        arcs=arcs,
        destinationFeatures=destination_features,
        epicenterFeatures=epicenter_features,
        nightLightsUrl=night_lights_url,
        viewState=view_state,
        colourTrigger=colour_trigger,
        height=height,
        key=key,
        default=None,
    )
