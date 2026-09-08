# Cloud Native DevSecOps Platform

This repository is a local development stack plus production-oriented AWS/EKS IaC. It demonstrates:

- a microservice-based backend
- a static frontend dashboard
- local container orchestration with Docker Compose
- CI/CD and GitOps starter files for AWS EKS deployment
- DevSecOps practices and Kubernetes manifests
- Terraform modules for RDS/Secrets Manager, ECR, S3/CloudFront OAC, networking, and EKS

## Included components

- User Service (FastAPI)
- Product Service (FastAPI)
- Order Service (FastAPI)
- Frontend (static HTML/JS served by Nginx)
- PostgreSQL and Keycloak for local auth/data dependencies
- Terraform and Kubernetes starter structure
- Jenkins pipeline for CI/CD automation

## Quick start

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:8080
- User Service: http://localhost:8001/docs
- Product Service: http://localhost:8002/docs
- Order Service: http://localhost:8003/docs
- Keycloak: http://localhost:8081

## Project layout

```text
project-root/
├── services/
│   ├── user-service/
│   ├── product-service/
│   └── order-service/
├── frontend/
├── infrastructure/
├── k8s-manifests/
├── jenkins/
├── docs/
├── .github/workflows/
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

## Infrastructure and AWS roadmap

This project includes both a local Docker Compose development environment and a Terraform-based AWS infrastructure plan. The implementation is intended to proceed in stages so the platform can be built safely and predictably.

### Recommended project flow

1. Run the project locally with Docker Compose
2. Validate backend, frontend, and database services
3. Design the AWS networking and EKS architecture
4. Implement Terraform modules one by one
5. Validate with `terraform validate` and `terraform plan`
6. Review the AWS plan before `terraform apply`
7. Deploy services to EKS
8. Integrate RDS, ECR, S3, and CloudFront
9. Add CI/CD automation and GitOps practices

### Terraform implementation order

```text
networking -> eks -> rds -> ecr -> s3-cloudfront -> dynamodb
```

This order is important because EKS depends on VPC and subnet outputs, while RDS should live inside private networking.

### Dev environment practices

- Use `t3.medium` or similar small worker nodes for low cost
- Use one NAT Gateway in dev to reduce cost
- Keep the database small and private
- Keep all resources tagged with Project, Environment, and ManagedBy

### Quick Terraform commands

```bash
cd infrastructure/terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file="../environments/dev/terraform.tfvars"
```

### Important rule

These commands only format and validate configuration (and optionally create a plan). Do not run `terraform apply` or `terraform destroy` from this repository without a manually reviewed plan and approved AWS credentials. Phase 11 requires manual AWS credential and `kubectl` verification; no deployment is claimed by this project.

Kubernetes image manifests use immutable digest placeholders. CI replaces them with digests from ECR and Argo CD syncs the committed GitOps state. Set the ACM certificate annotation through an environment promotion process; do not commit secrets.

## Notes

This repository is intentionally structured as a functional starter rather than a full production AWS deployment. It gives you a working local baseline that mirrors the architecture described in the original design brief, while also including the IaC, GitOps, and pipeline scaffolding you would extend for EKS and AWS.
