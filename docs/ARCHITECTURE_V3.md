# SAG V3 Architecture (Hybrid Agentic Search: SAG + RAG)

## Overview

SAG V3 extends the deterministic and RBAC-first foundation from V2 into a hybrid architecture:

- **SAG lane** for structured, high-trust, real-time data.
- **RAG lane** for unstructured document retrieval and semantic matching.
- **Agentic orchestration** for routing, ACL enforcement, re-ranking, and synthesis.

This design keeps V2 strengths (security, determinism, auditability) while improving recall and answer quality for mixed enterprise workloads.

## Hybrid Agentic Search Architecture Diagram

```mermaid
flowchart TD
    subgraph "Data Sources"
        A1[Web Forms / Applications\n(Structured Data)]
        A2[Excel Files\n(With Strict Template)]
        A3[Documents: PDF, Word, Policies]
        A4[Databases / APIs\n(Real-time Data)]
    end

    subgraph "Data Governance Layer\n(Root Cause Strategy)"
        DG[Data Governance Policy]
        DG -->|No vertical merged cells| A2
        DG -->|Highly volatile data -> Web Form| A1
        DG -->|Clean data only| Pipeline
    end

    subgraph "Ingestion Pipeline"
        Pipeline[Asynchronous Ingestion Pipeline]
        ETL[ETL Process\n(Excel -> Per-Person Chunks)]
        MD[Document -> Markdown Conversion]
        
        A1 --> Pipeline
        A2 --> ETL --> Pipeline
        A3 --> MD --> Pipeline
        A4 --> Pipeline
    end

    subgraph "Storage Layer"
        VectorDB[(Vector Database\n+ Embeddings)]
        IndexDB[(Elasticsearch\nInverted Index)]
        StructDB[(Structured DB / JSON\nfor SAG)]
    end

    subgraph "Hybrid Search Engine"
        Bot1[Bot 1: Query Router\nKeyword Swarm + Semantic Search]
        ACL[ACL Verification Layer\n(Permission Check)]
        ReRank[Re-ranking\n(Cross-Encoder)]
        Bot2[Bot 2: Reasoning Agent + Summarizer]
    end

    subgraph "Output"
        Answer[Final Answer with Source\n(SAG + RAG)]
    end

    %% Flow
    Pipeline --> VectorDB
    Pipeline --> IndexDB
    Pipeline --> StructDB
    
    User[User Query] --> Bot1
    
    Bot1 --> IndexDB
    Bot1 --> VectorDB
    Bot1 --> StructDB
    
    IndexDB & VectorDB & StructDB --> ACL
    ACL --> ReRank
    ReRank --> Bot2
    Bot2 --> Answer

    %% Style
    classDef governance fill:#FFF3CD,stroke:#DAA520
    classDef pipeline fill:#E3F2FD,stroke:#1976D2
    classDef storage fill:#F3E5F5,stroke:#7B1FA2
    classDef search fill:#E8F5E9,stroke:#388E3C
    
    class DG governance
    class Pipeline,ETL,MD pipeline
    class VectorDB,IndexDB,StructDB storage
    class Bot1,ACL,ReRank,Bot2 search
```

## Why this V3 model

- **Data Governance is top-level:** mitigate human input errors at source instead of fixing only downstream symptoms.
- **SAG path:** structured sources from forms/apps/DB provide deterministic and near real-time truth.
- **RAG path:** unstructured policy and document content is normalized to markdown and indexed semantically.
- **Hybrid orchestration:** route, fuse, and rank across deterministic and semantic candidates before synthesis.
- **Mandatory ACL gate:** every retrieval path must pass permission checks before answer generation.

## High-level view (for executives)

1. Govern data quality first.
2. Ingest both structured and unstructured enterprise data.
3. Search both deterministic and semantic indexes.
4. Enforce ACL before any content reaches reasoning.
5. Return explainable answers with authorized sources.

## Detailed technical view (for engineering teams)

1. **Ingestion**
   - Structured data from forms/APIs enters async pipeline directly.
   - Excel follows template-driven ETL and chunk normalization.
   - Documents convert to markdown for unified indexing.
2. **Indexing**
   - `StructDB`: deterministic lookups for SAG.
   - `IndexDB`: keyword/inverted index for lexical retrieval.
   - `VectorDB`: embedding search for semantic retrieval.
3. **Agentic retrieval**
   - `Bot1` routes query and executes hybrid candidate gathering.
   - ACL layer validates role, department, and file-level policy.
   - Cross-encoder reranker produces final context pack.
4. **Synthesis**
   - `Bot2` reasons only over ACL-approved context.
   - Output includes source grounding from both SAG and RAG lanes.

## Migration note from V2

V3 should be introduced with feature flags and backward compatibility:

- Keep V2 deterministic retrieval as baseline fallback.
- Enable hybrid retrieval in controlled rollout.
- Keep RBAC and per-file policy checks as hard gates.
