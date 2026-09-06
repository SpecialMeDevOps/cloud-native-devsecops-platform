# Infrastructure starter

This folder contains the Terraform and deployment scaffolding for the AWS/EKS architecture described in the project brief.

## Suggested modules

- networking
- eks
- rds
- dynamodb
- s3-cloudfront
- ecr

## Example layout

```text
infrastructure/
├── modules/
│   ├── networking/
│   ├── eks/
│   ├── rds/
│   └── s3/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── README.md
```

## Next step

Add the actual Terraform providers and resource definitions for VPC, EKS, RDS, S3, and CloudFront.
