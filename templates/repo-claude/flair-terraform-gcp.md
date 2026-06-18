# CLAUDE.md — flair-terraform-gcp

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Terraform 1.10+, Google provider ≥ 6.0  
**Role**: GCP infrastructure modules — GKE cluster, Cloud SQL PostgreSQL, Memorystore Redis, Artifact Registry, IAM workload identity, VPC  
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

# Plan (requires GCP credentials)
gcloud auth application-default login
terraform plan -var-file=envs/dev.tfvars

# Security scan
tflint --recursive
tfsec .
checkov -d .

# Docs
terraform-docs markdown . > README.md
```

---

## Repo structure

```
flair-terraform-gcp/
  modules/
    flair-gke/           ← GKE Autopilot cluster (workload identity)
    flair-cloudsql/      ← Cloud SQL PostgreSQL 17 (HA, private IP)
    flair-redis/         ← Memorystore Redis (HA)
    flair-registry/      ← Artifact Registry (Docker)
    flair-iam/           ← Service accounts + workload identity bindings
    flair-vpc/           ← VPC, subnets, VPC Service Controls, private service access
  envs/
    dev.tfvars
    staging.tfvars
    production.tfvars
  main.tf
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

- **`terraform apply` and `terraform destroy` forbidden for agents** — human approval required
- Use Workload Identity Federation for GKE pods — no service account key files
- Cloud SQL: private IP only (`authorized_networks = []`), SSL required
- GKE Autopilot preferred over Standard — no node management overhead
- All resources labeled: `project = "flair"`, `environment = var.environment`
- State in GCS bucket + object lock — never commit `.tfstate`
