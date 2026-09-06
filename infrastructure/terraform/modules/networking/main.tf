variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

output "private_subnet_ids" {
  value = ["subnet-00000000", "subnet-11111111"]
}
