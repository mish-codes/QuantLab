import json

import pytest

from handler import lambda_handler


def _event(body):
    return {"httpMethod": "POST", "body": json.dumps(body) if isinstance(body, dict) else body}


class TestLambdaHandler:
    def test_happy_path(self):
        response = lambda_handler(
            _event({"spot_curve": {"1Y": 4.0, "2Y": 5.0}}), None
        )
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "forward_curve" in body
        assert "1Y-2Y" in body["forward_curve"]
        assert body["forward_curve"]["1Y-2Y"] == pytest.approx(6.0096, abs=0.01)

    def test_missing_spot_curve_returns_400(self):
        response = lambda_handler(_event({}), None)
        assert response["statusCode"] == 400

    def test_empty_spot_curve_returns_400(self):
        response = lambda_handler(_event({"spot_curve": {}}), None)
        assert response["statusCode"] == 400

    def test_spot_curve_not_a_dict_returns_400(self):
        response = lambda_handler(_event({"spot_curve": [1, 2]}), None)
        assert response["statusCode"] == 400

    def test_malformed_json_returns_500(self):
        response = lambda_handler(_event("{not json"), None)
        assert response["statusCode"] == 500
