output "api_endpoint" {
  value       = "${aws_apigatewayv2_stage.dev.invoke_url}/curves/fit"
  description = "Full POST endpoint for curve fitting"
}

output "lambda_function_name" {
  value = aws_lambda_function.curve_fitting.function_name
}

output "lambda_function_arn" {
  value = aws_lambda_function.curve_fitting.arn
}

output "http_api_id" {
  value = aws_apigatewayv2_api.curves.id
}
