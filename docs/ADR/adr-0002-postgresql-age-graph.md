# ADR-0002 — PostgreSQL + Apache AGE as the single database engine

**Date**: 2026-06-18
**Status**: Accepted
**Deciders**: Database Architect, Go Software Architect

---

## Context

FLAIR needs both relational storage (users, agents, audit logs, configuration) and graph storage (flow topology, cross-zone path queries, service dependency chains). Using two separate database systems (e.g. PostgreSQL + Neo4j) would increase operational complexity for self-hosted deployments.

---

## Decision

Use a single PostgreSQL instance with the Apache AGE extension for graph capabilities. Relational data uses standard PostgreSQL tables. Graph data uses AGE's Cypher query interface on top of PostgreSQL.

The `GraphStore` interface abstracts the implementation — callers never import pgx or AGE directly.

---

## Alternatives considered

| Option | Pros | Cons |
|---|---|---|
| PostgreSQL + Neo4j | Best-in-class graph queries | Two databases to operate, two connection pools, licensing (Neo4j enterprise) |
| PostgreSQL + AGE (chosen) | Single database, single connection pool, Cypher support, open source | AGE is less mature than Neo4j, Cypher subset only |
| PostgreSQL only (adjacency list) | Simplest | Complex graph traversal queries, no Cypher |
| DGraph | Native graph + GraphQL | Unfamiliar operational model, smaller community |

---

## Consequences

- Self-hosted deployments need only one database — significantly reduces operational burden
- AGE extension must be installed on the PostgreSQL instance (`CREATE EXTENSION age`)
- AGE Cypher is a subset of Neo4j Cypher — not all Neo4j queries are portable
- No ORM — raw pgx only, because AGE requires direct SQL/Cypher via `cypher()` function
- Migration tooling: golang-migrate with plain SQL files

---

## Relation to FLAIR non-negotiables

Default install works without Kubernetes or third-party services — single PostgreSQL instance satisfies this constraint.
