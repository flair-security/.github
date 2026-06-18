# CLAUDE.md — flair-agent-k8s

> Repo-specific context.
> Read organisation CLAUDE.md first — it lives at `../flair-security/.github/CLAUDE.md`

---

## Quick reference

**Stack**: Go 1.24+, Kubernetes API (controller-runtime), eBPF (Cilium libs), DaemonSet  
**Role**: Kubernetes-native capture agent — pod metadata enrichment + eBPF flow capture per node → `Flow` structs  
**Licence**: BSL-1.1

---

## Build & test commands

```bash
# Build
go build ./...

# Unit tests
go test ./...

# Integration tests (requires kind cluster)
go test -tags integration ./...

# Deploy to kind (dry-run)
kubectl apply --dry-run=server -k manifests/

# Linter
golangci-lint run ./...

# Generate Kubernetes CRD manifests
controller-gen crd:generateEmbeddedObjectMeta=true paths="./..." output:crd:dir=manifests/crds
```

---

## Repo structure

```
flair-agent-k8s/
  cmd/flair-agent-k8s/    ← entrypoint, controller-runtime manager
  internal/
    collector/             ← eBPF collector (same pattern as flair-agent)
    k8s/                   ← pod watcher, namespace mapper, workload enricher
    enricher/              ← enriches Flow with ContainerID, pod labels
    ingest/                ← sends enriched flows to flair-core
    config/
  manifests/
    base/                  ← kustomize base (DaemonSet, RBAC, ServiceAccount)
    crds/                  ← generated CRD manifests
  api/
    v1alpha1/              ← FlairAgentConfig CRD types
```

---

## Key differences from flair-agent (bare metal)

| Aspect | flair-agent | flair-agent-k8s |
|---|---|---|
| Deployment | systemd | DaemonSet |
| Metadata | process name + PID | pod name + namespace + workload |
| Enrichment | ContainerID from cgroups | ContainerID + Kubernetes metadata |
| RBAC | n/a | ServiceAccount with pod list/watch |

`ContainerID` field in `Flow` struct populated by this agent only.

---

## Skills auto-loaded for this repo

| Priority | Skill | Trigger |
|---|---|---|
| 1 (always) | skill-solid-go | all US |
| 1 (always) | skill-error-handling | all US |
| 1 (always) | skill-ac-traceability | all US |
| 1 (always) | skill-ebpf-architecture | repo = flair-agent-k8s |
| 1 (always) | skill-observability | all US |
| 2 | skill-docker-deployment | DaemonSet / manifest changes |
| 2 | skill-authentication | mTLS / RBAC changes |

---

## Repo-specific rules

- DaemonSet hostPID and hostNetwork must be justified in the PR description — they are attack surface
- All Kubernetes API calls use controller-runtime client — never raw `k8s.io/client-go` in business logic
- RBAC manifests follow least privilege — only pod list/watch, no cluster-admin
- Never log pod annotations raw — may contain secrets from external-secrets injectors
