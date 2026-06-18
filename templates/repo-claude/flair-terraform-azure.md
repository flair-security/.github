# CLAUDE.md — flair-terraform-azure

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Terraform 1.10+, AzureRM provider ≥ 4.0  
**Role**: Azure infrastructure modules — AKS cluster, Azure Database for PostgreSQL, Azure Cache for Redis, ACR, Azure AD workload identity, VNet  
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

# Plan (requires Azure credentials)
az login
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
flair-terraform-azure/
  modules/
    flair-aks/           ← AKS cluster (workload identity, OIDC issuer, add-ons)
    flair-postgres/      ← Azure Database for PostgreSQL Flexible Server
    flair-redis/         ← Azure Cache for Redis (premium tier)
    flair-acr/           ← Azure Container Registry
    flair-identity/      ← Managed Identity + workload identity federation
    flair-vnet/          ← VNet, subnets, NSG, private endpoints
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

- **`terraform apply` and `terraform destroy` forbidden for agents** — human approval required in CI/CD
- No service principal client secrets in Terraform — use Managed Identity / workload identity
- All resources in a resource group tagged: `Project = "FLAIR"`, `Environment = var.environment`
- PostgreSQL: private endpoint only, no public network access
- AKS: workload identity enabled, pod security standards enforced (`restricted`)
- State in Azure Storage Account + container lease lock — never commit `.tfstate`
