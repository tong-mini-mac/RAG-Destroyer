# SAG V3 Test Report — ONNX Dense Embedding Benchmark

Date: 2026-04-27 (01:13)  
Environment: Windows 10 (PowerShell), Python 3.13.12, 8 GB RAM  
Pipeline: `VectorIndex.query()` (ONNX dense) → `HybridSearch.rerank()`  
Model: `all-MiniLM-L6-v2` (384-dim) via `sentence-transformers`  
No LLM keyword generation. No `.md` lexical search. No SearchWorker.

## Scope

- Validate ONNX dense embedding pipeline (`SAG_ENABLE_ONNX_EMBEDDING=true`)
- Measure department classification accuracy at scale (20/50/80/100 paraphrase questions)
- Compare against token-set cosine baseline (Mode A)
- Determine whether ONNX provides meaningful accuracy improvement to justify its 4× RAM cost

## Pipeline (as tested)

```
User Query
  → VectorIndex.query()              ← ONNX dense cosine similarity (all-MiniLM-L6-v2)
  → HybridSearch.rerank_vector_only() ← department/phrase boost + R&C penalty
  → Department classification from top result
```

No LLM calls — benchmark measures **raw vector retrieval accuracy only**.

## Benchmark Results

| Size | Pass | Fail | Pass Rate | Vector | Rerank | RAM Peak |
|:---|:---|:---|:---|:---|:---|:---|
| **20Q** | 19 | 1 | **95.0%** | 684 ms | 0.06 ms | 483 MB |
| **50Q** | 47 | 3 | **94.0%** | 58 ms | 0.06 ms | 486 MB |
| **80Q** | 69 | 11 | **86.2%** | 62 ms | 0.06 ms | 487 MB |
| **100Q** | 86 | 14 | **86.0%** | 65 ms | 0.06 ms | 488 MB |

Note: 20Q time includes first-inference model loading (~620 ms). Subsequent sizes exclude loading.

## Failure Analysis (100Q — 14 failures)

| # | Query (truncated) | Expected | Got | Failure Pattern |
|---|-------------------|----------|-----|-----------------|
| 1 | delinquency monitoring and follow-up | Credit & Loans | R&C | `delinquency` → R&C vector match stronger |
| 2 | cyber-security controls for core banking system | IT & Digital | R&C | `security` + `control` → R&C dominates |
| 3 | software release and rollback safeguards | IT & Digital | R&C | `release` + `safeguards` → R&C |
| 4 | server patching and vulnerability review | IT & Digital | R&C | `vulnerability` → R&C dominates |
| 5 | change management for production systems | IT & Digital | Operations | Semantic drift to operations vocabulary |
| 6 | privileged-access reviews for infrastructure admin | IT & Digital | HR & Admin | `review` → HR match |
| 7 | vulnerability remediation SLA tracking | IT & Digital | HR & Admin | `remediation` → HR match |
| 8 | backup and disaster recovery validation | IT & Digital | R&C | `disaster recovery` → R&C |
| 9 | audit findings prioritized and remediated | R&C | Operations | `audit` → Operations match |
| 10 | organization-wide schedule guidance | General | HR & Admin | `schedule` + `guidance` → HR |
| 11 | general policy note shared across departments | General | HR & Admin | `policy` → HR |
| 12 | branch fraud alerts escalation | Operations | R&C | `fraud` + `risk` → R&C |
| 13 | incident postmortem and corrective action | IT & Digital | R&C | `incident` → R&C |
| 14 | infrastructure configuration baselines control | IT & Digital | R&C | `baseline` + `control` → R&C |

**Root cause:** all-MiniLM-L6-v2 (384-dim) does not provide sufficient discrimination for short corporate chunks (~1.2 KB avg). Semantic vectors for `security`, `risk`, `vulnerability`, `incident`, `audit` cluster together, producing the same R&C dominance pattern as token-set cosine.

## Accuracy Comparison (All Modes)

| Mode | Description | 20Q | 50Q | 80Q | 100Q | Avg/Query | RAM |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **A** | Vector-only (token-set, no LLM) | 90.0% | 90.0% | 88.75% | **90.0%** | ~24 ms | ~110 MB |
| **B** | Full pipeline (lexical, no LLM) | 95.0% | 90.0% | 86.25% | 87.0% | ~135 ms | ~110 MB |
| **C** | LLM pipeline (lexical + vector) | 95.0% | 98.0% | 95.0% | **92.0%** | ~545 ms | ~113 MB |
| **D** | Vector-only via Orchestrator (LLM kw) | 95.0% | 90.0% | 87.5% | 86.0% | ~1,094 ms | ~110 MB |
| **E** | **ONNX dense** (this run) | **95.0%** | **94.0%** | **86.2%** | **86.0%** | **~65 ms** | **~488 MB** |

## Key Findings

1. **ONNX accuracy = token-set accuracy** — at 100Q, both achieve 86.0%. all-MiniLM-L6-v2 does not provide a meaningful advantage over zero-dependency token-set cosine for this dataset.
2. **RAM 4.4× higher** — sentence-transformers + numpy array push from ~110 MB to ~488 MB.
3. **Latency 2.7× higher** — ~65 ms vs ~24 ms per query (excluding first-load).
4. **R&C dominance persists** — dense embeddings still cluster security/risk vocabulary together, producing the same cross-department misclassification pattern.

## Risks / Limitations

- **all-MiniLM-L6-v2 is too small** (384-dim) for discriminating short corporate chunks with overlapping vocabulary.
- **Chunk content is too sparse** — only chunk `content` is embedded; richer text (tags + summary + title embedded separately) may improve discrimination.
- **Model loading cost** — first query pays ~620 ms for loading sentence-transformers (cached after first use).
- **Not recommended for production** with current config — token-set cosine provides same accuracy with zero dependencies and lower cost.

## Revised Recommendations

1. **Keep ONNX disabled by default** (`SAG_ENABLE_ONNX_EMBEDDING=false`). Zero benefit to justify 4× RAM.
2. **If pursuing dense embeddings:** try a larger model (`all-mpnet-base-v2`, 768-dim) or multilingual model (`intfloat/multilingual-e5-small`). Enrich chunk embedding text with tags + summary + title.
3. **Higher-impact path to break 90% ceiling:** enrich chunk context, add document-level embeddings, tighten R&C penalty threshold, or reintroduce metadata signals from `_SEARCH_CACHE.json`.
4. **LLM pipeline (Mode C)** remains the highest-accuracy path at 92% with moderate latency (~545 ms).

## Benchmark Artifacts

- Results JSON: `tmp/e2e_onnx_benchmark.json`
- Test script: `scripts/benchmark_onnx.py`
- Baseline (Mode D): `tmp/e2e_vector_orch_benchmark.json`
- LLM pipeline: `tmp/e2e_llm_v4.json`
