variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "repository_names" {
  description = "ECR repositories to create."
  type        = set(string)
}

resource "aws_ecr_repository" "service" {
  for_each             = var.repository_names
  name                 = "${var.environment}/${each.value}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  force_delete = false
}

resource "aws_ecr_lifecycle_policy" "service" {
  for_each   = aws_ecr_repository.service
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Retain the newest 30 tagged images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v", "sha-"]
          countType     = "imageCountMoreThan"
          countNumber   = 30
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Expire untagged images after seven days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

output "repository_urls" {
  description = "ECR repository URLs keyed by service name."
  value       = { for name, repository in aws_ecr_repository.service : name => repository.repository_url }
}

output "repository_arns" {
  description = "ECR repository ARNs keyed by service name."
  value       = { for name, repository in aws_ecr_repository.service : name => repository.arn }
}
