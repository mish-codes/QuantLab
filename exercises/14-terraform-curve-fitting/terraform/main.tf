# Curve-fitting Lambda + HTTP API as Terraform-managed resources.
#
# Scope is intentionally narrow: this config only manages resources that
# DID NOT EXIST before. The existing S3 bucket (finbytes-quant-lab-data),
# the shared IAM role (quant-lab-lambda-role), and the existing REST API
# (5wsgaoptef, with bootstrap/forwards routes) were created manually in
# earlier exercises and stay outside Terraform's state.
#
# Going forward, any *new* infrastructure is Terraform-managed.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Local state for now. If you want remote state later, uncomment and
  # create the bucket via `aws s3 mb s3://finbytes-quant-lab-tfstate`.
  # backend "s3" {
  #   bucket = "finbytes-quant-lab-tfstate"
  #   key    = "exercises/14-curve-fitting/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

# --- Lambda function ---
#
# 512MB is generous for scipy's optimiser; 60s timeout for Nelder-Mead
# convergence on larger inputs.

resource "aws_lambda_function" "curve_fitting" {
  function_name = "${var.project_name}-curve-fitting"
  runtime       = "python3.11"
  handler       = "handler.lambda_handler"
  role          = var.lambda_role_arn
  timeout       = 60
  memory_size   = 512

  filename         = "${path.module}/../src/deployment.zip"
  source_code_hash = filebase64sha256("${path.module}/../src/deployment.zip")
}

# --- HTTP API (API Gateway v2) ---
#
# HTTP APIs are cheaper + simpler than REST APIs. We use a fresh one
# here to keep curve-fitting separate from the REST API that hosts
# bootstrap/forwards. The two APIs can coexist without conflict.

resource "aws_apigatewayv2_api" "curves" {
  name          = "${var.project_name}-curves-http"
  protocol_type = "HTTP"
  description   = "HTTP API for curve fitting and future curve endpoints"
}

resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.curves.id
  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "curve_fitting" {
  api_id                 = aws_apigatewayv2_api.curves.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.curve_fitting.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "fit" {
  api_id    = aws_apigatewayv2_api.curves.id
  route_key = "POST /curves/fit"
  target    = "integrations/${aws_apigatewayv2_integration.curve_fitting.id}"
}

# Let API Gateway invoke the Lambda. Wildcard allows any stage/route
# on this specific API.
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGWInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.curve_fitting.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.curves.execution_arn}/*/*"
}
