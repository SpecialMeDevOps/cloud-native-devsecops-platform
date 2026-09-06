variable "environment" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

output "cluster_name" {
  value = "${var.environment}-cluster"
}
