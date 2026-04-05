variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
  default     = "quant-lab"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "quant-lab"
}

variable "lambda_role_arn" {
  description = "ARN of the existing Lambda execution role (created manually)"
  type        = string
  default     = "arn:aws:iam::349348221529:role/quant-lab-lambda-role"
}
