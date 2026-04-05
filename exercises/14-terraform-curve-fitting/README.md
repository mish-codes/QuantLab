# Exercise 14 — Terraform + Nelson-Siegel / Svensson

Parametric yield curve fitting, deployed via Terraform.

## What this deploys

- **Lambda function:** `quant-lab-curve-fitting` (python3.11, 512MB, scipy)
- **HTTP API:** `quant-lab-curves-http` with route `POST /curves/fit`
- Reuses the existing `quant-lab-lambda-role` (created manually earlier)

These are **new** resources. Terraform does NOT touch the existing S3
bucket, the shared IAM role, or the REST API with the bootstrap/forwards
routes — those stay outside Terraform's state.

## Prerequisites

```bash
# Install Terraform
winget install HashiCorp.Terraform
terraform --version  # should show 1.5+

# AWS CLI profile `quant-lab` with RDS/Lambda/APIGW permissions
aws sts get-caller-identity --profile quant-lab
```

## Deploy steps

**1. Build the Lambda deployment zip (includes scipy).**

scipy + numpy binaries must match Lambda's architecture (`x86_64` + manylinux).
Easiest way is to pull them from a Linux Docker image:

```bash
cd src
docker run --rm -v "$PWD":/out public.ecr.aws/lambda/python:3.11 \
  bash -c "pip install numpy scipy -t /out/package && \
           cp /out/handler.py /out/curve_fitting.py /out/package/ && \
           cd /out/package && zip -r ../deployment.zip ."
```

(If you don't have Docker, `pip install numpy scipy -t package/` locally
works for dev but may fail at runtime with "invalid ELF" — the wheels
must be built for Linux x86_64.)

**2. Run Terraform.**

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Terraform outputs include `api_endpoint` — copy that URL.

**3. Test the live endpoint.**

```bash
curl -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{
    "model": "svensson",
    "maturities": [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0],
    "yields":     [4.80, 4.90, 5.10, 5.20, 5.15, 4.90, 4.70, 4.50, 4.40, 4.45]
  }'
```

**4. Tear it down later.**

```bash
cd terraform
terraform destroy
```

That removes the Lambda + HTTP API but leaves the shared role and S3
bucket intact.

## State

Local state file (`terraform.tfstate`) lives in `terraform/` and is
gitignored. For a team project you'd move this to a remote backend
(S3 + DynamoDB lock); the backend block is commented out in `main.tf`
for when you're ready.
