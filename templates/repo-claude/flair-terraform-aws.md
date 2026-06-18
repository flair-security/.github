# CLAUDE.md — flair-terraform-aws

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Terraform 1.10+, AWS provider ≥ 5.80  
**Role**: AWS infrastructure modules — EKS cluster, RDS PostgreSQL, ElastiCache Redis, ECR, IAM, VPC  
**Licence**: Apache-2.0

---

## Build & test commands

```bash
# Init
terraform init

# Validate
terraform validate

# Format check
terraform fmt -check -recursive

# Format fix
terraform fmt -recursive

# Plan (requires AWS credentials)
terraform plan -var-file=envs/dev.tfvars

# Security scan (no AWS creds needed)
tflint --recursive
tfsec .
checkov -d .

# Docs generation
terraform-docs markdown . > README.md
```

---

## Repo structure

```
flair-terraform-aws/
  modules/
    flair-eks/          ← EKS cluster (managed node groups, IRSA, add-ons)
    flair-rds/          ← RDS PostgreSQL 17 (Multi-AZ, automated backups)
    flair-redis/        ← ElastiCache Redis (cluster mode)
    flair-ecr/          ← ECR repositories per FLAIR service
    flair-iam/          ← IAM roles (least privilege per service)
    flair-vpc/          ← VPC, subnets, security groups
  envs/
    dev.tfvars
    staging.tfvars
    production.tfvars
  main.tf               ← module composition for a full FLAIR stack
  variables.tf
  outputs.tf
  versions.tf
```

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-devops-cicd | all US |
| 1 (always) | skill-ac-traceability | all US |

---

## Repo-specific rules

- **`terraform apply` and `terraform destroy` are FORBIDDEN for agents** — only CI/CD pipeline (requires human approval step)
- No hardcoded account IDs, region names, or AMI IDs — use data sources or variables
- All resources tagged: `project = "flair"`, `env = var.environment`, `managed_by = "terraform"`
- IAM policies follow least privilege — no `"*"` Actions or Resources without documented justification
- RDS and Redis in private subnets only — no public endpoint
- State stored in S3 + DynamoDB lock — never commit `.tfstate` files
