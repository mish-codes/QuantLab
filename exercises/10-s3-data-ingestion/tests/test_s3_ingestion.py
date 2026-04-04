import json
import pytest
import boto3
from datetime import date
from unittest.mock import patch, MagicMock
from moto import mock_aws
from s3_ingestion import (
    upload_yields_to_s3,
    download_yields_from_s3,
    list_available_dates,
    ingest_daily_yields,
)

BUCKET = "test-quant-lab-data"
PREFIX = "par-yields"


@pytest.fixture
def s3_bucket():
    """Create a mock S3 bucket for testing."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET)
        yield s3


class TestUploadYields:
    def test_uploads_json_to_correct_key(self, s3_bucket):
        yields = {"1M": 5.25, "10Y": 4.30, "30Y": 4.45}
        target_date = date(2026, 4, 4)

        upload_yields_to_s3(
            yields=yields,
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=target_date,
            s3_client=s3_bucket,
        )

        key = f"{PREFIX}/2026-04-04.json"
        response = s3_bucket.get_object(Bucket=BUCKET, Key=key)
        body = json.loads(response["Body"].read())
        assert body["date"] == "2026-04-04"
        assert body["yields"]["10Y"] == 4.30

    def test_upload_includes_metadata(self, s3_bucket):
        yields = {"1M": 5.25, "10Y": 4.30}
        target_date = date(2026, 4, 4)

        upload_yields_to_s3(
            yields=yields,
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=target_date,
            s3_client=s3_bucket,
        )

        key = f"{PREFIX}/2026-04-04.json"
        response = s3_bucket.get_object(Bucket=BUCKET, Key=key)
        body = json.loads(response["Body"].read())
        assert body["source"] == "FRED"
        assert body["num_maturities"] == 2


class TestDownloadYields:
    def test_downloads_and_parses_json(self, s3_bucket):
        data = {
            "date": "2026-04-04",
            "source": "FRED",
            "num_maturities": 2,
            "yields": {"1M": 5.25, "10Y": 4.30},
        }
        s3_bucket.put_object(
            Bucket=BUCKET,
            Key=f"{PREFIX}/2026-04-04.json",
            Body=json.dumps(data),
        )

        result = download_yields_from_s3(
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=date(2026, 4, 4),
            s3_client=s3_bucket,
        )

        assert result["yields"]["10Y"] == 4.30

    def test_missing_date_raises(self, s3_bucket):
        with pytest.raises(FileNotFoundError, match="2099-01-01"):
            download_yields_from_s3(
                bucket=BUCKET,
                prefix=PREFIX,
                as_of=date(2099, 1, 1),
                s3_client=s3_bucket,
            )


class TestListAvailableDates:
    def test_lists_dates_from_keys(self, s3_bucket):
        for d in ["2026-04-01", "2026-04-02", "2026-04-03"]:
            s3_bucket.put_object(
                Bucket=BUCKET,
                Key=f"{PREFIX}/{d}.json",
                Body=json.dumps({"date": d, "yields": {}}),
            )

        dates = list_available_dates(
            bucket=BUCKET, prefix=PREFIX, s3_client=s3_bucket
        )

        assert len(dates) == 3
        assert date(2026, 4, 1) in dates
        assert date(2026, 4, 3) in dates

    def test_empty_bucket_returns_empty_list(self, s3_bucket):
        dates = list_available_dates(
            bucket=BUCKET, prefix=PREFIX, s3_client=s3_bucket
        )
        assert dates == []


class TestIngestDailyYields:
    @patch("s3_ingestion.fetch_par_yields")
    def test_fetches_and_uploads(self, mock_fetch, s3_bucket):
        mock_fetch.return_value = {"1M": 5.25, "10Y": 4.30}

        result = ingest_daily_yields(
            api_key="fake-key",
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=date(2026, 4, 4),
            s3_client=s3_bucket,
        )

        assert result["date"] == "2026-04-04"
        assert result["num_maturities"] == 2

        downloaded = download_yields_from_s3(
            bucket=BUCKET,
            prefix=PREFIX,
            as_of=date(2026, 4, 4),
            s3_client=s3_bucket,
        )
        assert downloaded["yields"]["10Y"] == 4.30
