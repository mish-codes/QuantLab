import json

from handler import lambda_handler


def _event(body):
    return {"body": json.dumps(body) if isinstance(body, dict) else body}


class TestLambdaHandler:
    def test_nelson_siegel_happy_path(self):
        response = lambda_handler(_event({
            "model": "nelson-siegel",
            "maturities": [0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            "yields": [4.80, 4.70, 4.50, 4.30, 4.15, 4.25, 4.45],
        }), None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["model"] == "nelson-siegel"
        assert "beta0" in body["params"]
        assert "lambda" in body["params"]
        assert len(body["fitted"]) == 7
        assert body["rmse"] < 0.2

    def test_svensson_happy_path(self):
        response = lambda_handler(_event({
            "model": "svensson",
            "maturities": [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0],
            "yields": [4.80, 4.90, 5.10, 5.20, 5.15, 4.90, 4.70, 4.50, 4.40, 4.45],
        }), None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["model"] == "svensson"
        assert "beta3" in body["params"]

    def test_length_mismatch_returns_400(self):
        response = lambda_handler(_event({
            "maturities": [1.0, 2.0, 5.0],
            "yields": [4.0, 4.2],
        }), None)
        assert response["statusCode"] == 400

    def test_too_few_points_returns_400(self):
        response = lambda_handler(_event({
            "maturities": [1.0, 2.0],
            "yields": [4.0, 4.2],
        }), None)
        assert response["statusCode"] == 400

    def test_non_list_inputs_return_400(self):
        response = lambda_handler(_event({"maturities": 1, "yields": 2}), None)
        assert response["statusCode"] == 400

    def test_unknown_model_returns_400(self):
        response = lambda_handler(_event({
            "model": "magic",
            "maturities": [1.0, 2.0, 3.0, 5.0],
            "yields": [4.0, 4.2, 4.3, 4.5],
        }), None)
        assert response["statusCode"] == 400

    def test_malformed_json_returns_500(self):
        response = lambda_handler(_event("{not json"), None)
        assert response["statusCode"] == 500
