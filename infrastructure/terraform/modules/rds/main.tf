variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "subnet_ids" {
  description = "Private subnet IDs for the DB subnet group."
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID for the database security group."
  type        = string
}

variable "allowed_security_group_ids" {
  description = "Security groups allowed to connect to PostgreSQL."
  type        = list(string)
  default     = []
}

variable "instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}

variable "engine_version" {
  description = "PostgreSQL engine version."
  type        = string
  default     = "16.4"
}

variable "allocated_storage" {
  description = "Initial allocated storage in GiB."
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Initial PostgreSQL database name."
  type        = string
  default     = "platform"
}

variable "master_username" {
  description = "Initial PostgreSQL master username."
  type        = string
  default     = "platform_admin"
}

resource "aws_security_group" "rds" {
  name        = "${var.environment}-rds"
  description = "Restrict PostgreSQL access to EKS worker security groups."
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from approved EKS security groups"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-postgres"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.environment}-postgres-subnet-group"
  }
}

resource "aws_db_instance" "main" {
  identifier                  = "${var.environment}-postgres"
  engine                      = "postgres"
  engine_version              = var.engine_version
  instance_class              = var.instance_class
  allocated_storage           = var.allocated_storage
  max_allocated_storage       = 100
  storage_type                = "gp3"
  storage_encrypted           = true
  db_name                     = var.database_name
  username                    = var.master_username
  manage_master_user_password = true
  port                        = 5432
  db_subnet_group_name        = aws_db_subnet_group.main.name
  vpc_security_group_ids      = [aws_security_group.rds.id]
  publicly_accessible         = false
  multi_az                    = true
  backup_retention_period     = 7
  deletion_protection         = true
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.environment}-postgres-final"
  copy_tags_to_snapshot       = true
  auto_minor_version_upgrade  = true
  apply_immediately           = false
}

output "db_identifier" {
  description = "RDS instance identifier."
  value       = aws_db_instance.main.identifier
}

output "db_endpoint" {
  description = "RDS endpoint address."
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS listener port."
  value       = aws_db_instance.main.port
}

output "secret_arn" {
  description = "AWS-managed Secrets Manager ARN containing the RDS master credentials."
  value       = aws_db_instance.main.master_user_secret[0].secret_arn
}
