# Architecture overview

This project implements a lightweight version of the cloud-native DevSecOps platform described in the blueprint.

## Runtime components

- Frontend: static SPA served through Nginx
- API Layer: three FastAPI microservices
- Data layer: PostgreSQL for local persistence
- Identity: Keycloak for authentication flow
- Messaging: prepared for SQS/SNS integration in AWS deployments
- Observability: metrics endpoints and recommended Prometheus/Grafana setup

## Service responsibilities

### User Service

- manages profiles and auth-related user records
- exposes health, user listing, and user creation endpoints

### Product Service

- keeps the catalog and product metadata
- exposes CRUD-like contract for inventory data

### Order Service

- handles customer orders
- validates users and products through service-to-service HTTP calls
- stores order state and status information

## Deployment path

This starter repo is designed to extend naturally into:

- Docker Compose for local dev
- Kubernetes manifests for GitOps deployment
- Terraform modules for AWS EKS networking and infrastructure
- Jenkins or GitHub Actions for CI/CD automation
- Trivy, SonarQube, OPA, and monitoring stacks in later stages

## Security posture

The project includes placeholders and conventions for:

- JWT/OIDC integration via Keycloak
- environment-based secrets
- service-to-service validation
- network segmentation via Kubernetes policy and ingress

This is intentionally a starter baseline, not a full production cloud deployment.
