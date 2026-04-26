"""Benchmark ONNX dense embeddings: VectorIndex.query() + HybridRerank.
Uses all 100 questions from paraphrase_100_results_after_boost.json.
"""
import os
os.environ["SAG_ENABLE_ONNX_EMBEDDING"] = "True"

import sys, json, time, psutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core import Utils
import importlib
importlib.reload(Utils)
from core.VectorIndex import VectorIndex
from core.HybridSearch import HybridSearchEngine

# ── Load all 100 questions ──────────────────────────────────────
q_path = os.path.join(os.path.dirname(__file__), "..", "tmp", "paraphrase_100_results_after_boost.json")
with open(q_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = data["rows"]
all_questions = [
    {"query": r["query"].strip(), "expected": r["expect_department"]}
    for r in rows
]
print(f"Loaded {len(all_questions)} questions from {os.path.basename(q_path)}")

sizes = [20, 50, 80, 100]

# ── Init ────────────────────────────────────────────────────────
vi = VectorIndex()
if not vi.enable_onnx:
    print("ERROR: ONNX not enabled!")
    sys.exit(1)
hybrid = HybridSearchEngine(alpha=0.65, top_k=5)

# ── Benchmark loops ──────────────────────────────────────────────
results_out = []
for size in sizes:
    questions = all_questions[:size]
    n_pass = 0
    failures = []
    timing_vector = 0.0
    timing_rerank = 0.0
    proc = psutil.Process()
    ram_vals = []

    for item in questions:
        q = item["query"]
        expected = item["expected"]

        t0 = time.perf_counter()
        vector_hits = vi.query(q, "ALL", top_k=8)
        t1 = time.perf_counter()
        timing_vector += (t1 - t0)

        t2 = time.perf_counter()
        reranked = hybrid.rerank_vector_only(q, vector_hits) if vector_hits else []
        t3 = time.perf_counter()
        timing_rerank += (t3 - t2)

        dept = reranked[0].get("department") if reranked else (vector_hits[0].get("department") if vector_hits else None)
        if dept == expected:
            n_pass += 1
        else:
            top3 = []
            for h in (reranked or vector_hits)[:3]:
                top3.append({
                    "title": h.get("title", ""),
                    "dept": h.get("department", ""),
                    "score": round(float(h.get("vector_score", 0)), 4),
                })
            failures.append({
                "query": q, "expected": expected, "got": dept,
                "top3": top3,
            })

        ram_vals.append(proc.memory_info().rss / 1048576)

    avg_vector_ms = (timing_vector / size) * 1000
    avg_rerank_ms = (timing_rerank / size) * 1000
    pass_rate = round(n_pass / size * 100, 1)
    n_fail = size - n_pass

    results_out.append({
        "size": size,
        "pass": n_pass,
        "fail": n_fail,
        "pass_rate": pass_rate,
        "avg_vector_ms": round(avg_vector_ms, 2),
        "avg_rerank_ms": round(avg_rerank_ms, 2),
        "total_ms": round((timing_vector + timing_rerank) * 1000, 2),
        "ram_start_mb": round(ram_vals[0], 3) if ram_vals else 0,
        "ram_peak_mb": round(max(ram_vals), 3) if ram_vals else 0,
        "failures": failures,
    })

    print(f"\nSize={size:>3d}: {n_pass}/{size} pass ({pass_rate}%)  "
          f"Vector={avg_vector_ms:>5.2f}ms  Rerank={avg_rerank_ms:>4.2f}ms  "
          f"Failures={n_fail}")
    for f in failures:
        print(f"  ✗ {f['query'][:65]:65s}  expected={f['expected']:20s}  got={f['got']}")

# ── Summary ──────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("  BENCHMARK SUMMARY — ONNX DENSE EMBEDDINGS (all-MiniLM-L6-v2)")
print(f"{'='*60}")
for r in results_out:
    print(f"  Size={r['size']:>3d}  {r['pass']:>2d}/{r['size']:>3d} pass ({r['pass_rate']:>4.1f}%)  "
          f"Vector={r['avg_vector_ms']:>5.2f}ms  Rerank={r['avg_rerank_ms']:>4.2f}ms  "
          f"RAM peak={r['ram_peak_mb']:>5.1f}MB")

# ── Save ─────────────────────────────────────────────────────────
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "tmp"), exist_ok=True)
out_path = os.path.join(os.path.dirname(__file__), "..", "tmp", "e2e_onnx_benchmark.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "onnx_dense_embeddings",
        "results": results_out,
    }, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {out_path}")
