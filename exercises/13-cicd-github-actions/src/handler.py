"""AWS Lambda handler for the forward-rate endpoint.

POST body: {"spot_curve": {"1Y": 4.0, "2Y": 5.0, ...}}
Response:  {"forward_curve": {"1Y-2Y": 6.0096, ...}}
"""

import json

from forward_rates import calculate_forward_rates


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        spot_curve = body.get("spot_curve")
        if not isinstance(spot_curve, dict) or not spot_curve:
            return _response(400, {"error": "spot_curve must be a non-empty object"})
        return _response(200, {"forward_curve": calculate_forward_rates(spot_curve)})
    except json.JSONDecodeError as exc:
        return _response(500, {"error": f"invalid JSON: {exc}"})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
