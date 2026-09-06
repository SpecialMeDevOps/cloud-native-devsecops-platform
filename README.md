# Cloud Native DevSecOps Platform

This repository is a starter implementation aligned to the architecture described in the attached project brief. It focuses on a working local development stack that demonstrates:

- a microservice-based backend
- a static frontend dashboard
- local container orchestration with Docker Compose
- CI/CD and GitOps starter files for AWS EKS deployment
- DevSecOps practices and Kubernetes manifests

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

## Notes

This repository is intentionally structured as a functional starter rather than a full production AWS deployment. It gives you a working local baseline that mirrors the architecture described in the original design brief, while also including the IaC, GitOps, and pipeline scaffolding you would extend for EKS and AWS.
