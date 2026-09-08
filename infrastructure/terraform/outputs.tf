output "ecr_repository_urls" {
  description = "ECR repository URLs keyed by service."
  value       = module.ecr.repository_urls
}

output "database_secret_arn" {
  description = "Secrets Manager ARN for generated PostgreSQL credentials."
  value       = module.rds.secret_arn
}

output "database_endpoint" {
  description = "Private PostgreSQL endpoint."
  value       = module.rds.db_endpoint
}

output "frontend_bucket_name" {
  description = "Private S3 bucket for frontend assets."
  value       = module.s3_cloudfront.bucket_name
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution hostname."
  value       = module.s3_cloudfront.distribution_domain_name
}
