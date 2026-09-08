# Infrastructure and AWS Deployment Guide

This folder contains production-oriented Terraform modules for the AWS-based cloud architecture. The code is intentionally declarative: this repository does not contain AWS credentials and no deployment is performed by validation or CI.

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

## Phases 2-10 implemented

The root stack now wires networking and EKS to:

- private, encrypted, Multi-AZ PostgreSQL RDS with generated credentials in Secrets Manager
- immutable, scan-on-push ECR repositories with lifecycle policies
- a private versioned S3 frontend bucket and CloudFront Origin Access Control
- root variables and outputs for database, registry, and CDN integration

Kubernetes manifests include a frontend, AWS Load Balancer Controller ingress, immutable digest placeholders, service hardening, and NetworkPolicies. Replace the zero digests and `${ACM_CERTIFICATE_ARN}` in an environment-specific promotion workflow; never commit credentials or certificate private keys.

## Prerequisites and validation

Before you run Terraform, make sure the following are ready:

- AWS account with permissions to create VPC, EKS, RDS, IAM, S3, CloudFront, etc.
- AWS CLI installed and configured
- Terraform installed (version >= 1.6)
- kubectl and the AWS Load Balancer Controller installed for a real EKS rollout
- an ACM certificate in `us-east-1` when using CloudFront aliases; the ALB certificate must be in the ALB region
- An AWS profile or environment variables set:

```bash
aws configure
# or
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

### Configure environment values

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
rds_instance_class = "db.t4g.micro"
rds_database_name = "platform"
rds_master_username = "platform_admin"
# acm_certificate_arn = "arn:aws:acm:us-east-1:..."
# cloudfront_aliases = ["platform.example.com"]
```

Keep dev cost-conscious by using smaller instance sizes and single NAT gateway.

### Initialize Terraform

From the Terraform directory:

```bash
cd infrastructure/terraform
terraform init
```

### Validate syntax and dependencies

```bash
terraform fmt -recursive
terraform validate
```

This confirms the modules are syntactically valid before creating AWS resources.

### Review the plan before apply

```bash
terraform plan -var-file="../environments/dev/terraform.tfvars"
```

Important:

- Never run `terraform apply` without reviewing the plan
- Check for unexpected VPC CIDRs, region choices, or resource counts
- Make sure NAT Gateway and EKS node sizing match your budget

### Module order

The correct order for implementation is:

1. networking
2. eks
3. rds
4. ecr
5. s3-cloudfront
6. dynamodb

This order matters because EKS depends on networking subnets and RDS depends on the VPC/private subnet layout.

### Module responsibilities

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

## Phase 11: manual verification only

Phase 11 is deliberately not automated here. An operator must supply AWS credentials, review a Terraform plan, and verify `kubectl` access to the intended cluster before any apply or Argo CD sync. Then verify EKS nodes, the RDS secret mount, ECR image pulls, ALB HTTPS health, and CloudFront content. Do not treat `terraform validate`, pytest, or client-side manifest checks as evidence that AWS resources were deployed.

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
13. Phase 11: manual AWS credentials and plan review
14. terraform apply (manual, after approval)
15. Deploy application workloads and verify with kubectl
```

## Notes

- Do not run `terraform apply` until the plan is reviewed.
- The dev environment should remain low-cost by default.
- Terraform validation and local tests are safe pre-deployment checks; they do not create or destroy resources.
