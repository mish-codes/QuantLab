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

import os
from pathlib import Path

import streamlit.components.v1 as components

_FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

# Streamlit Cloud was returning the "trouble loading the component"
# banner with ``path=`` — it wasn't serving our bundled index.html /
# world_night.jpg reliably for the app running out of a subdirectory.
# Workaround: host the frontend via jsDelivr (which already mirrors
# every file in the public repo) and use ``url=``. Streamlit then just
# points the iframe at the jsDelivr URL; the component protocol
# (``streamlit:componentReady`` + ``streamlit:render`` postMessages)
# works identically regardless of host. Image references inside
# index.html stay relative (``./world_night.jpg``) and resolve against
# the jsDelivr host, which serves the JPG from the same directory.
#
# Override via QL_CONTAGION_GLOBE_URL for dev (e.g., localhost dev
# server) or QL_CONTAGION_GLOBE_USE_PATH=1 to force the old path=
# behaviour against a local Streamlit.
_JSDELIVR_URL = (
    "https://cdn.jsdelivr.net/gh/mish-codes/QuantLab@master/"
    "dashboard/lib/components/contagion_globe/frontend/index.html"
)

_override_url = os.environ.get("QL_CONTAGION_GLOBE_URL")
_use_path = os.environ.get("QL_CONTAGION_GLOBE_USE_PATH") == "1"

if _override_url:
    _component_func = components.declare_component("contagion_globe", url=_override_url)
elif _use_path:
    _component_func = components.declare_component("contagion_globe", path=str(_FRONTEND_DIR))
else:
    _component_func = components.declare_component("contagion_globe", url=_JSDELIVR_URL)


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
