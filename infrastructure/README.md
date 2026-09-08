# Infrastructure and AWS Deployment Guide

This folder contains the Terraform IaC for the AWS-based cloud architecture of the Cloud Native DevSecOps Platform. It is designed to complement the local Docker Compose setup and eventually provision a production-ready AWS environment for EKS, RDS, ECR, S3, CloudFront, and DynamoDB.

## Current project structure

```text
infrastructure/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── versions.tf
│   └── modules/
│       ├── networking/
│       ├── eks/
│       ├── rds/
│       ├── s3-cloudfront/
│       ├── dynamodb/
│       └── ecr/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── README.md
```

## What this infrastructure is meant to create

The Terraform code should eventually provision:

- VPC with public and private subnets
- Internet Gateway and NAT Gateway
- EKS cluster with managed node group
- RDS PostgreSQL instance in private subnets
- ECR repositories for user-service, product-service, and order-service
- S3 static site bucket + CloudFront distribution
- DynamoDB table (schema to be finalized)
- DevOps-ready tagging, least-privilege IAM, and environment-specific defaults

## Step-by-step implementation roadmap

### 1. Prerequisites

Before you run Terraform, make sure the following are ready:

- AWS account with permissions to create VPC, EKS, RDS, IAM, S3, CloudFront, etc.
- AWS CLI installed and configured
- Terraform installed (version >= 1.6)
- An AWS profile or environment variables set:

```bash
aws configure
# or
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

### 2. Configure environment values

Use the environment tfvars file for dev defaults:

```hcl
# infrastructure/environments/dev/terraform.tfvars
aws_region = "us-east-1"
environment = "dev"
vpc_cidr = "10.10.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]
public_subnet_cidrs = ["10.10.1.0/24", "10.10.2.0/24"]
private_subnet_cidrs = ["10.10.11.0/24", "10.10.12.0/24"]
single_nat_gateway = true
```

Keep dev cost-conscious by using smaller instance sizes and single NAT gateway.

### 3. Initialize Terraform

From the Terraform directory:

```bash
cd infrastructure/terraform
terraform init
```

### 4. Validate syntax and dependencies

```bash
terraform fmt -recursive
terraform validate
```

This confirms the modules are syntactically valid before creating AWS resources.

### 5. Review the plan before apply

```bash
terraform plan -var-file="../environments/dev/terraform.tfvars"
```

Important:

- Never run `terraform apply` without reviewing the plan
- Check for unexpected VPC CIDRs, region choices, or resource counts
- Make sure NAT Gateway and EKS node sizing match your budget

### 6. Implement each module in order

The correct order for implementation is:

1. networking
2. eks
3. rds
4. ecr
5. s3-cloudfront
6. dynamodb

This order matters because EKS depends on networking subnets and RDS depends on the VPC/private subnet layout.

### 7. Module responsibilities

#### networking

- Create VPC
- Create public and private subnets in multiple AZs
- Create Internet Gateway and NAT Gateway
- Create route tables and route associations
- Export `vpc_id`, `public_subnet_ids`, and `private_subnet_ids`

#### eks

- Create EKS cluster
- Create managed node group
- Create IAM roles and policies
- Enable OIDC provider for IRSA
- Export cluster metadata

#### rds

- Create PostgreSQL database in private subnets
- Attach DB subnet group and security group
- Accept credentials via AWS Secrets Manager
- Export host and port

#### ecr

- Create repositories for `user-service`, `product-service`, and `order-service`
- Enable image scanning on push

#### s3-cloudfront

- Create static website bucket
- Configure CloudFront distribution
- Use Origin Access Control for secure access

#### dynamodb

- Keep table schema generic until finalized
- Use configurable partition key and on-demand billing as a safe default

### 8. Tagging and security standards

All AWS resources should include:

```hcl
default_tags = {
  Project   = "Cloud-Native-Microservices-DevOps-Project"
  Environment = "dev"
  ManagedBy = "Terraform"
}
```

Also follow least-privilege IAM and restrict database access to only the required security groups or service roles.

### 9. Validate the environment after deployment

Once `terraform apply` is successful, validate:

- EKS cluster is in ACTIVE state
- Worker nodes join the cluster
- RDS instance is reachable from EKS
- ECR repositories are created
- S3 + CloudFront static site responds correctly

### 10. Next actions for the repository

After the Terraform stack is complete, the next phases are:

- deploy application manifests to EKS
- configure Kubernetes secrets and configmaps
- wire services to RDS and ECR
- set up CI/CD pipeline for image builds and deployments
- harden security with IAM, vulnerability scanning, and GitOps workflow

## Recommended execution order for this project

```text
1. Configure AWS credentials
2. Review dev tfvars
3. terraform init
4. terraform validate
5. terraform plan
6. Implement networking module
7. Implement EKS module
8. Implement RDS module
9. Implement ECR module
10. Implement S3 + CloudFront module
11. Implement DynamoDB module
12. Review final plan
13. terraform apply (manual, after approval)
14. Deploy application workloads
```

## Notes

- Do not run `terraform apply` until the plan is reviewed.
- The dev environment should remain low-cost by default.
- The current implementation is a scaffold and should be completed module by module before production use.
