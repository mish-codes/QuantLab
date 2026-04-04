"""S3 ingestion pipeline for US Treasury par yield data.

Fetches daily yields from FRED, stores as dated JSON in S3 under
`<prefix>/YYYY-MM-DD.json`, and provides read/list helpers.
"""

import json
from datetime import date, timedelta

import boto3
from fredapi import Fred


# FRED series IDs -> human-readable maturity labels.
# Duplicated from exercise 09 so this module is self-contained.
TREASURY_SERIES = {
    "DGS1MO": "1M",
    "DGS3MO": "3M",
    "DGS6MO": "6M",
    "DGS1": "1Y",
    "DGS2": "2Y",
    "DGS3": "3Y",
    "DGS5": "5Y",
    "DGS7": "7Y",
    "DGS10": "10Y",
    "DGS20": "20Y",
    "DGS30": "30Y",
}


def fetch_par_yields(api_key: str, as_of: date | None = None) -> dict[str, float]:
    """Fetch US Treasury par yields from FRED.

    Looks back up to 7 days to handle weekends and holidays when FRED
    does not publish a value.
    """
    fred = Fred(api_key=api_key)
    target = as_of or date.today()
    start = target - timedelta(days=7)

    yields = {}
    for series_id, label in TREASURY_SERIES.items():
        data = fred.get_series(
            series_id, observation_start=start, observation_end=target
        )
        data = data.dropna()
        if len(data) > 0:
            yields[label] = round(float(data.iloc[-1]), 2)
    return yields


def upload_yields_to_s3(
    yields: dict[str, float],
    bucket: str,
    prefix: str,
    as_of: date,
    s3_client=None,
) -> dict:
    """Upload par yield data to S3 as a dated JSON object.

    The object is stored at `<prefix>/YYYY-MM-DD.json` with a simple
    envelope containing the date, source, count and raw yields.
    Returns the envelope that was uploaded.
    """
    s3 = s3_client or boto3.client("s3")

    data = {
        "date": as_of.isoformat(),
        "source": "FRED",
        "num_maturities": len(yields),
        "yields": yields,
    }

    key = f"{prefix}/{as_of.isoformat()}.json"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2),
        ContentType="application/json",
    )

    return data


def download_yields_from_s3(
    bucket: str,
    prefix: str,
    as_of: date,
    s3_client=None,
) -> dict:
    """Download par yield data from S3 for a given date.

    Raises FileNotFoundError if no object exists for that date.
    """
    s3 = s3_client or boto3.client("s3")
    key = f"{prefix}/{as_of.isoformat()}.json"

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response["Body"].read())
    except s3.exceptions.NoSuchKey:
        raise FileNotFoundError(f"No yield data for {as_of.isoformat()}")
    except Exception as e:
        if "NoSuchKey" in str(e):
            raise FileNotFoundError(f"No yield data for {as_of.isoformat()}")
        raise


def list_available_dates(
    bucket: str,
    prefix: str,
    s3_client=None,
) -> list[date]:
    """List all dates with yield data stored under the given prefix."""
    s3 = s3_client or boto3.client("s3")

    response = s3.list_objects_v2(Bucket=bucket, Prefix=f"{prefix}/")
    if "Contents" not in response:
        return []

    dates = []
    for obj in response["Contents"]:
        filename = obj["Key"].split("/")[-1]
        if filename.endswith(".json"):
            date_str = filename.replace(".json", "")
            try:
                dates.append(date.fromisoformat(date_str))
            except ValueError:
                continue  # skip keys that don't match our naming

    return sorted(dates)


def ingest_daily_yields(
    api_key: str,
    bucket: str,
    prefix: str,
    as_of: date | None = None,
    s3_client=None,
) -> dict:
    """Fetch yields from FRED for a date and upload them to S3.

    Returns the envelope that was written to S3.
    """
    target = as_of or date.today()
    yields = fetch_par_yields(api_key=api_key, as_of=target)
    return upload_yields_to_s3(
        yields=yields,
        bucket=bucket,
        prefix=prefix,
        as_of=target,
        s3_client=s3_client,
    )
