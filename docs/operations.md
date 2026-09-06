# Operations notes

## Local verification

Run the stack:

```bash
docker compose up --build
```

Check health endpoints:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## Future AWS hardening tasks

- enable ECR image signing
- enforce OPA policy checks on manifests
- use AWS Secrets Manager or Vault for credentials
- configure CloudFront and WAF ahead of production release
- attach Prometheus/Grafana/Loki stacks to your cluster

## Recommended next steps

1. Add PostgreSQL models and migrations per service.
2. Add JWT validation middleware to API gateways and service boundaries.
3. Add Kafka or SQS event contracts for order and inventory updates.
4. Add Helm charts and ArgoCD applications.
5. Add Terraform modules for VPC, EKS, RDS, and S3/CloudFront.
