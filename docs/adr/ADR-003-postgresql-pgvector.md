# ADR-003: PostgreSQL with pgvector Over Dedicated Vector Database

**Status**: Accepted
**Date**: 2026-02-19
**Context**: RinggitSense Database Architecture

## Decision

Use PostgreSQL 15 with the pgvector extension for both relational data and vector similarity search, rather than adding a dedicated vector database (Pinecone, Weaviate, Qdrant, etc.).

## Context

RinggitSense will need vector operations for:
- AG-05 Query Agent: Semantic search over transactions (finding relevant transactions for natural language queries)
- AG-01 Categorizer: Category similarity lookup for ambiguous transactions
- Future: Merchant name deduplication via embedding similarity

## Rationale

### 1. Operational Simplicity

One database to manage, backup, monitor, and deploy. For a solo-developer project, every additional service is operational burden.

| Approach | Services to Manage |
|----------|-------------------|
| PostgreSQL + pgvector | 1 (PostgreSQL) |
| PostgreSQL + Pinecone | 2 (PostgreSQL + Pinecone SaaS) |
| PostgreSQL + Qdrant | 2 (PostgreSQL + Qdrant container) |

### 2. Performance Is Adequate at Our Scale

pgvector benchmarks show:
- <10ms query time for 100K vectors (768 dimensions)
- <50ms for 1M vectors with HNSW index
- RinggitSense MVP target: <100K vectors (10K users × ~10 embeddings each)

We are far below the scale where a dedicated vector DB provides meaningful performance advantage.

### 3. Transactional Consistency

With pgvector, vector operations participate in the same ACID transactions as relational data. Inserting a transaction and its embedding is atomic — no eventual consistency concerns.

### 4. Cost

| Service | Monthly Cost (MVP scale) |
|---------|------------------------|
| pgvector (same PostgreSQL instance) | $0 additional |
| Pinecone Starter | $0 (limited) / $70+ (production) |
| Weaviate Cloud | $25+ |
| Self-hosted Qdrant | Container overhead |

### 5. Migration Path

If RinggitSense scales beyond 1M vectors or needs specialized vector features (multi-tenancy, filtered search at massive scale), we can:
1. Export embeddings from pgvector
2. Import into a dedicated vector DB
3. Route vector queries to the new service
4. Keep relational queries on PostgreSQL

The data model doesn't change — only the query routing.

## Consequences

- Docker image uses `pgvector/pgvector:pg15` instead of `postgres:15-alpine`
- Need to run `CREATE EXTENSION vector;` in migration
- Vector indexes (HNSW or IVFFlat) must be created explicitly
- Limited to pgvector's feature set (no built-in hybrid search, no automatic reranking)

## Alternatives Considered

1. **Pinecone**: Best-in-class vector search but adds SaaS dependency, cost, and data residency concerns (Malaysian financial data). Rejected.
2. **Weaviate**: Feature-rich but overkill for our scale. Rejected.
3. **Qdrant**: Good self-hosted option but adds another container to manage. Deferred.
4. **No vector search**: Limits AG-05 to keyword search only. Rejected — semantic search is a key differentiator.
