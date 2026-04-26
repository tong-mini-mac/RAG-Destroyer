# SAG Metadata Schema (YAML Front Matter)

This document defines the recommended YAML front matter contract for markdown files under `knowledge/<Department>/`.

## Purpose

- Keep retrieval deterministic and auditable.
- Improve keyword and hybrid rerank quality.
- Preserve policy controls (`audience`, RBAC filters).

## Required Fields (Recommended Minimum)

```yaml
---
title: "Human-readable document title"
doc_id: "HRA-001"
department: "HR & Admin"
tags: ["hr", "benefits", "policy"]
summary: "Short English summary used for retrieval preview."
---
```

## Full Supported Fields

```yaml
---
title: "Employee Welfare and Leave Policy 2026"
doc_id: "HRA-001"
category: "Policy"
department: "HR & Admin"
related_departments: ["General", "Operations"]
tags: ["hr", "welfare", "leave", "benefits"]
summary: "Defines leave types, allowance rules, and approval flow."
audience: "all"
---
```

## Field-by-Field Specification

- `title` (string)
  - Display title and primary lexical signal.
  - Keep concise and business-readable.

- `doc_id` (string)
  - Stable document identifier (example: `GEN-001`, `HRA-014`).
  - Used in citations and auditability.

- `category` (string, optional)
  - High-level grouping (example: `Policy`, `Procedure`, `Guideline`).

- `department` (string)
  - Must match a configured silo folder in `config/org_structure.json`.

- `related_departments` (array of strings, optional)
  - Cross-reference hints; does not override RBAC.

- `tags` (array of strings)
  - Keywords used by deterministic search and hybrid reranking.

- `summary` (string)
  - Short retrieval summary. Prefer one paragraph.

- `audience` (string, optional)
  - Access intent for role filtering.
  - Supported normalized values:
    - `all` (default if missing)
    - `management` (hidden from `Operational Staff`)

## Audience Normalization Rules

Implementation (`core/Utils.py`) normalizes audience roughly as:

- Treated as `all`:
  - missing/empty values
  - `all`, `everyone`, `public`, `staff`, `operational`
- Treated as `management`:
  - `management`, `manager`, `executive`, `leadership`, `heads`, `confidential`
- Unknown values fallback to `all`

## Authoring Guidelines

- Use English for `title` and `summary` to maximize retrieval consistency.
- Keep `summary` factual; avoid long narrative blocks.
- Prefer specific tags (`loan-policy`, `aml`, `leave-approval`) over generic ones (`document`, `info`).
- Do not encode secrets in front matter.

## Validation Checklist

Before indexing:

1. File is under `knowledge/<Department>/`.
2. `department` matches the folder/silo.
3. `doc_id` is unique enough for your governance process.
4. `tags` is a list, not a comma-joined string.
5. `audience` is intentional (`all` vs `management`).

## Notes for V3 Hybrid

- Chunk/vector metadata is generated at indexing time (not authored manually) in:
  - `_CHUNK_INDEX.json`
  - `_VECTOR_INDEX.json`
- `table` and `code` chunks are excluded from vector eligibility by policy.
