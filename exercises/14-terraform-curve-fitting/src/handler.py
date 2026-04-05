"""AWS Lambda handler for curve fitting.

API Gateway v2 (HTTP API) passes a simpler event than v1:
    {"version": "2.0", "body": "...", ...}

Accepts either model="nelson-siegel" or model="svensson".

POST body:
    {
        "model": "svensson",
        "maturities": [0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
        "yields": [4.80, 4.70, 4.50, 4.30, 4.15, 4.25, 4.45]
    }

Response:
    {
        "model": "svensson",
        "params": {...},
        "fitted": [...],
        "rmse": 0.04
    }
"""

import json

import numpy as np

from curve_fitting import fit_nelson_siegel, fit_svensson


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        model = body.get("model", "nelson-siegel")
        maturities = body.get("maturities")
        yields = body.get("yields")

        if not isinstance(maturities, list) or not isinstance(yields, list):
            return _response(400, {"error": "maturities and yields must be arrays"})
        if len(maturities) != len(yields):
            return _response(400, {"error": "maturities and yields length mismatch"})
        if len(maturities) < 4:
            return _response(400, {"error": "need at least 4 observations to fit"})

        m_arr = np.array(maturities, dtype=float)
        y_arr = np.array(yields, dtype=float)

        if model == "svensson":
            params, fitted, rmse = fit_svensson(m_arr, y_arr)
        elif model in ("nelson-siegel", "ns"):
            params, fitted, rmse = fit_nelson_siegel(m_arr, y_arr)
        else:
            return _response(400, {"error": f"unknown model: {model!r}"})

        return _response(200, {
            "model": model,
            "params": params,
            "fitted": [round(float(v), 4) for v in fitted],
            "rmse": round(rmse, 4),
        })

    except json.JSONDecodeError as exc:
        return _response(500, {"error": f"invalid JSON: {exc}"})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
