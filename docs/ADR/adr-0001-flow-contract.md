# ADR-0001 — Flow struct as the central cross-repo contract

**Date**: 2026-06-18
**Status**: Accepted
**Deciders**: Go Software Architect, eBPF Expert, Angular Frontend Expert

---

## Context

FLAIR is a multi-repo ecosystem where agents (producers) send flow data to flair-core (consumer/storage), which then exposes it to flair-ui (display). Without a formal contract, each repo could evolve its data model independently, causing silent breaking changes and desynchronisation between components.

---

## Decision

The `Flow` Go struct in `flair-core/domain/flow.go` is the authoritative definition of the flow data contract. All agents must produce `Flow` values conforming to this definition. flair-ui TypeScript interfaces in `domain/flow.model.ts` must mirror this struct exactly.

Any change to the `Flow` struct is a breaking change requiring:
1. An ADR (this document as template)
2. Coordinated PRs: agent → core → ui, opened simultaneously
3. Label `flow-contract` on all PRs — triggers human review

Optional fields (`ContainerID`, `JA3Hash`, `TLSCipherSuite`) use Go zero values — never block a minimal agent implementation.

`Metadata map[string]string` is intentionally open for extensibility without breaking the contract.

---

## Alternatives considered

| Option | Pros | Cons |
|---|---|---|
| Protobuf/gRPC contract | Strong typing, auto-generated clients | Adds build toolchain complexity, harder to contribute to |
| JSON schema in a shared repo | Language-agnostic | No compile-time enforcement, drift risk |
| Go struct (chosen) | Compile-time enforcement for Go repos, simple | TypeScript interface must be maintained manually |

---

## Consequences

- New fields added to `Flow` are non-breaking if they have zero values and are optional
- Removed fields or type changes are breaking — require major version bump via Semantic Release
- flair-ui `flow.model.ts` must be updated in the same PR as `flair-core/domain/flow.go`
- Skill `flair-ac-traceability` and `skill-solid-go` enforce this via Gate 1 hard block

---

## Relation to FLAIR non-negotiables

Direct — the Flow contract is listed as a non-negotiable in `CLAUDE.md`.
Breaking changes are a Gate 4 hard block until cross-repo PRs are coordinated.
