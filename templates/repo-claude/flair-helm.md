# CLAUDE.md — flair-helm

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Helm 3.17+, Helmfile 0.168+, Kubernetes ≥ 1.29  
**Role**: Kubernetes deployment — Helm charts for all FLAIR components  
**Licence**: Apache-2.0

---

## Build & test commands

```bash
# Lint all charts
helm lint charts/*

# Template render (dry-run)
helm template flair charts/flair-core -f environments/dev/values.yaml

# Diff against cluster (requires kubeconfig)
helm diff upgrade flair-core charts/flair-core -f environments/staging/values.yaml

# Helmfile diff (all releases)
helmfile diff -e staging

# Validate templates
helm template flair charts/flair-core | kubectl apply --dry-run=client -f -

# Schema validation
helm lint charts/flair-core --strict
```

---

## Repo structure

```
flair-helm/
  charts/
    flair-agent/         ← DaemonSet chart (Linux agent)
    flair-agent-k8s/     ← DaemonSet chart (Kubernetes-native agent)
    flair-core/          ← Deployment chart (stateful: PostgreSQL, Redis deps)
    flair-ui/            ← Deployment chart (nginx + Angular SPA)
    flair-rules/         ← ConfigMap chart (scoring rules)
  environments/
    dev/                 ← values.yaml per chart
    staging/
    production/
  helmfile.yaml          ← orchestrates all releases
```

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-devops-cicd | all US |
| 1 (always) | skill-ac-traceability | all US |
| 2 | skill-docker-deployment | image tag / resource changes |

---

## Repo-specific rules

- **Never commit `helm upgrade` or `helm install` commands** — chart changes are applied by CD pipeline only
- Production values files contain no secrets — use sealed-secrets or external-secrets references
- Resource requests/limits required on all containers — no empty resource blocks
- All charts have `artifacthub.io` annotations in `Chart.yaml`
- Chart versions follow SemVer — bump `version` on every change, `appVersion` when image tag changes
