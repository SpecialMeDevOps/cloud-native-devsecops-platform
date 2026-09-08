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

## How to apply this project step by step

Use the project in this order so the stack can be started safely and predictably:

### 1. Start the local application stack

This is the quickest way to test the full repo locally before you deploy to AWS or Kubernetes.

```bash
docker compose up --build
```

Verify the stack:

```bash
docker compose ps
curl http://localhost:8080
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

To stop everything:

```bash
docker compose down -v
```

### 2. Apply the Kubernetes manifests

For a cluster deployment, apply the namespace and application resources in order:

```bash
kubectl apply -f k8s-manifests/namespace.yaml
kubectl apply -f k8s-manifests/user-service.yaml
kubectl apply -f k8s-manifests/product-service.yaml
kubectl apply -f k8s-manifests/order-service.yaml
kubectl apply -f k8s-manifests/frontend.yaml
kubectl apply -f k8s-manifests/ingress.yaml
kubectl apply -f k8s-manifests/network-policy.yaml
```

Or apply the whole Kustomize stack in one command:

```bash
kubectl apply -k k8s-manifests
```

Check results:

```bash
kubectl get ns
kubectl get pods -n cloud-platform
kubectl get svc -n cloud-platform
kubectl get ingress -n cloud-platform
```

### 3. Apply the AWS infrastructure with Terraform

This phase creates the VPC, EKS, RDS, Secrets Manager, ECR, and CloudFront resources.

```bash
Set-Location infrastructure/terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file="../environments/dev/terraform.tfvars"
```

If the plan looks correct, then apply it:

```bash
terraform apply -var-file="../environments/dev/terraform.tfvars"
```

Important: only run `terraform apply` after reviewing the plan and confirming the AWS account, region, networking, and cost profile are acceptable.

### 4. Connect to the EKS cluster and deploy the app

After the AWS infrastructure exists:

```bash
aws eks update-kubeconfig --region us-east-1 --name dev-cluster
kubectl get nodes
kubectl apply -k k8s-manifests
kubectl get pods -n cloud-platform
kubectl get ingress -n cloud-platform
```

The Ingress and ALB will only work once the AWS Load Balancer Controller and ACM certificate are configured.

### 5. Enable the Jenkins DevSecOps pipeline

Before enabling publishing, configure the required Jenkins credentials:

```text
aws-ecr-publisher
gitops-write-token
cosign-private-key
```

Then create or update the pipeline from [jenkins/Jenkinsfile](jenkins/Jenkinsfile). For a simple in-cluster Jenkins deployment, you can also apply [k8s-manifests/jenkins.yaml](k8s-manifests/jenkins.yaml).

Recommended path:

```text
1. Keep PUBLISH_IMAGES=false
2. Run scan-only builds
3. Review Trivy output and image security reports
4. Enable publishing after the results are approved
5. Trigger the GitOps manifest update only when the ECR digest is valid
```

### 6. Apply Argo CD GitOps sync

After cluster and repo access are ready:

```bash
kubectl apply -f k8s-manifests/argocd-app.yaml
kubectl -n argocd get applications
kubectl -n argocd get application cloud-platform
```

Expected state: `Synced` and `Healthy` once the ECR digests and cluster prerequisites are valid.

### 7. Production-style verification checklist

Run the following after every environment change:

```bash
pytest -q
kubectl get pods -n cloud-platform
kubectl get svc -n cloud-platform
kubectl get ingress -n cloud-platform
kubectl -n argocd get application cloud-platform
```

For local checks, confirm the frontend and service health endpoints before moving to AWS deployment.

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

## Complete implementation roadmap

The target workflow is:

```text
git push
  -> Jenkins webhook
  -> tests and security scans
  -> Docker images with immutable tags
  -> ECR
  -> GitOps manifest update
  -> Argo CD
  -> EKS
  -> AWS Load Balancer
  -> HTTPS public application
```

The repository changes are organized into these phases:

```text
Phase 1  Repository audit
Phase 2  RDS PostgreSQL + Secrets Manager
Phase 3  ECR repositories
Phase 4  S3 + CloudFront
Phase 5  Frontend Kubernetes deployment
Phase 6  Immutable ECR image digests
Phase 7  ALB + HTTPS
Phase 8  Kubernetes security hardening
Phase 9  Jenkins DevSecOps pipeline
Phase 10 Argo CD GitOps
Phase 11 Manual AWS deployment and verification
```

### Phase 1: Audit and prerequisites

Install and configure:

- AWS CLI with an AWS profile
- Terraform >= 1.6
- Docker Desktop
- Python 3.12
- `kubectl`
- `helm`
- Jenkins agent tools: Docker, AWS CLI, Trivy, Syft, Cosign, and Kustomize

Check local tools:

```powershell
aws --version
terraform version
docker --version
kubectl version --client
helm version
```

Never commit `.env`, `.pem`, `.key`, `.tfstate`, `.terraform/`, or credentials. See [.gitignore](.gitignore).

### Phase 2: RDS PostgreSQL and Secrets Manager

Terraform creates:

- Private DB subnet group
- Encrypted PostgreSQL RDS instance
- Non-public RDS security group
- PostgreSQL access only from the EKS node security group
- AWS-managed RDS master credentials in Secrets Manager
- Backups and deletion protection

Configuration is in [modules/rds/main.tf](infrastructure/terraform/modules/rds/main.tf).

Verify the module without creating AWS resources:

```powershell
Set-Location infrastructure/terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file="../environments/dev/terraform.tfvars"
```

Expected result: validation succeeds and the plan shows RDS, subnet group, security group, and Secrets Manager-related changes. Do not apply until the plan is reviewed.

Important: Terraform state can contain sensitive values. Use an encrypted remote backend before a shared or production deployment.

### Phase 3: ECR repositories

The ECR module creates immutable, scan-on-push repositories for:

- `user-service`
- `product-service`
- `order-service`
- `frontend`

Configuration is in [modules/ecr/main.tf](infrastructure/terraform/modules/ecr/main.tf).

Expected result after an approved apply: each repository exists under the selected environment prefix and rejects mutable tag reuse.

### Phase 4: S3 and CloudFront

The S3/CloudFront module creates:

- Private encrypted and versioned frontend bucket
- CloudFront Origin Access Control
- Bucket policy allowing reads only through CloudFront
- HTTPS redirect
- Optional custom ACM certificate and DNS aliases

Configuration is in [modules/s3-cloudfront/main.tf](infrastructure/terraform/modules/s3-cloudfront/main.tf).

For a custom CloudFront certificate, the ACM certificate must be issued in `us-east-1`.

### Phase 5: Frontend Kubernetes deployment

The frontend is deployed by [frontend.yaml](k8s-manifests/frontend.yaml). Nginx serves the static UI and proxies:

```text
/api/users    -> user-service:8001
/api/products -> product-service:8002
/api/orders   -> order-service:8003
```

This keeps backend services internal to the cluster. The frontend uses same-origin API paths instead of hardcoded localhost URLs.

### Phase 6: Immutable ECR image tags

[kustomization.yaml](k8s-manifests/kustomization.yaml) uses ECR image digests instead of `:latest`.

The CI flow is:

1. Build an image tagged with the Jenkins build identifier.
2. Push it to ECR.
3. Read the resulting digest from ECR.
4. Update the Kustomize image reference.
5. Commit the GitOps change.
6. Let Argo CD deploy the committed digest.

The zero-value digests in the repository are placeholders only. Jenkins must replace them before deployment.

### Phase 7: ALB and HTTPS

[ingress.yaml](k8s-manifests/ingress.yaml) configures the AWS Load Balancer Controller with:

- Internet-facing ALB
- IP target mode
- HTTP to HTTPS redirect
- ACM certificate annotation
- Frontend as the public entry point

Before applying it, replace `${ACM_CERTIFICATE_ARN}` through a deployment-time substitution process. Do not commit certificate material or private keys.

The AWS Load Balancer Controller and its IRSA role must be installed in the EKS cluster before this Ingress can create an ALB.

### Phase 8: Kubernetes security hardening

The service manifests include:

- Non-root users
- Dropped Linux capabilities
- `RuntimeDefault` seccomp
- Read-only root filesystems
- CPU and memory requests/limits
- Readiness and liveness probes
- Immutable image pull policy

[network-policy.yaml](k8s-manifests/network-policy.yaml) provides default-deny behavior and explicit platform traffic rules.

Review the policies in a staging cluster before production because CNI/network-policy behavior must be verified in the selected EKS configuration.

### Phase 9: Jenkins DevSecOps pipeline

[Jenkinsfile](jenkins/Jenkinsfile) defines:

1. Checkout
2. Unit tests
3. Python compile and optional Ruff quality checks
4. Trivy filesystem SAST/SCA/secret scan
5. Docker image builds
6. SBOM generation with Syft
7. Trivy image scans
8. Optional ECR publishing
9. Optional Cosign signing
10. GitOps digest update

Configure these Jenkins credentials before enabling publishing:

```text
aws-ecr-publisher
gitops-write-token
cosign-private-key
```

For an in-cluster Jenkins instance, [jenkins.yaml](k8s-manifests/jenkins.yaml) provides a simple Deployment and Service with HTTP and agent ports plus readiness/liveness checks against `/login`.

The `PUBLISH_IMAGES` parameter is intentionally false by default. Start with scans only, then enable publishing after reviewing the results.

### Phase 10: Argo CD GitOps

[argocd-app.yaml](k8s-manifests/argocd-app.yaml) configures:

- The repository as the source of truth
- `k8s-manifests` as the application path
- Automated sync
- Pruning of removed resources
- Self-healing
- Namespace creation

Install Argo CD and create the Application only after the EKS cluster and repository access are ready:

```powershell
kubectl apply -f k8s-manifests/argocd-app.yaml
kubectl -n argocd get applications
kubectl -n argocd get application cloud-platform
```

Expected result: the application becomes `Synced` and `Healthy` after valid ECR digests and cluster prerequisites are available.

### Phase 11: Manual deployment and verification

This phase requires explicit AWS access and is not run automatically by this repository.

1. Review variables:

```powershell
Get-Content infrastructure/environments/dev/terraform.tfvars
```

2. Initialize and validate:

```powershell
Set-Location infrastructure/terraform
terraform init
terraform validate
terraform plan -var-file="../environments/dev/terraform.tfvars" -out=dev.tfplan
```

3. Inspect the plan and confirm costs, region, CIDRs, RDS settings, NAT gateways, and EKS size.

4. Apply only after approval:

```powershell
terraform apply dev.tfplan
```

5. Configure kubeconfig:

```powershell
aws eks update-kubeconfig --region us-east-1 --name dev-cluster
kubectl get nodes
kubectl get pods -n cloud-platform
```

6. Verify application resources:

```powershell
kubectl get ingress -n cloud-platform
kubectl get svc -n cloud-platform
kubectl get events -n cloud-platform --sort-by=.lastTimestamp
kubectl -n argocd get application cloud-platform
```

7. Open the ALB hostname over HTTPS after DNS and ACM are configured.

Expected results:

- EKS cluster is `ACTIVE`
- Nodes are `Ready`
- Pods are `Running` and pass probes
- Argo CD is `Synced` and `Healthy`
- Ingress has an ALB hostname
- HTTPS returns the frontend
- Backend API paths work through the frontend proxy

Do not run `terraform destroy` in a shared or production environment. Keep the generated plan file and Terraform state out of Git.

## Local verification checklist

Run these before opening a pull request:

```powershell
pytest -q
Set-Location infrastructure/terraform
terraform fmt -check -recursive
terraform validate
Set-Location ../..
```

Expected result:

```text
8 passed
Success! The configuration is valid.
```

## Cost and safety notes

- Development uses a single NAT Gateway by default.
- Development uses small EKS and RDS sizes.
- RDS is private and deletion protection is enabled.
- ECR tags are immutable.
- No AWS resource is created by validation commands.
- Review every Terraform plan before applying.
- Never commit secrets, private keys, state files, or provider binaries.

## Current limitations

- Terraform apply has not been run from this repository.
- AWS Load Balancer Controller installation is a cluster prerequisite.
- DNS and ACM certificate validation are environment-specific.
- Jenkins credentials and agents must be configured by the platform operator.
- Application services still require a deliberate database persistence migration before claiming full production readiness.
