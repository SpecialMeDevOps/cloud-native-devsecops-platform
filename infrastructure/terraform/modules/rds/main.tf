variable "environment" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

output "db_identifier" {
  value = "${var.environment}-postgres"
}
