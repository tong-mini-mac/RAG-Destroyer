# Implementation Plan: Industrial Batch Refinement

Currently, the documents are located in the `raw_data/` folder but are not visible in the `knowledge/` vault because the **Registrar Bot** is processing them sequentially. With **500 files** detected, this process is critically slow.

## User Review Required

> [!IMPORTANT]
> **Cost & Scale Warning**: Processing all 500 files through an LLM (Gemini/OpenAI) will consume a significant amount of API tokens. 
> - **Option A**: Process all 500 files immediately using Parallel Refinement.
> - **Option B**: Process a small "Golden Batch" (e.g., 20 files) for demonstration purposes and leave the rest for on-demand processing.

## Proposed Changes

### 1. Data Refinery Parallelization
#### [MODIFY] [Refinery.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/Refinery.py)
- Implement `concurrent.futures.ThreadPoolExecutor` in the `scan_and_refine_all` method.
- Add a `max_workers` parameter (default: 4) to balance speed and API rate limits.
- Implement a thread-safe registry counter for document IDs.

### 2. Vault Indexing Optimization
#### [MODIFY] [VaultWarden.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/VaultWarden.py)
- Ensure the Indexer runs only *after* a batch is completed to avoid file-system locks during parallel writes.

## Verification Plan

### Automated Tests
- Run a benchmark test on 5 files and verify sub-second concurrent processing.
- Verify that `knowledge/_MASTER_INDEX.md` correctly lists all newly refined files.

### Manual Verification
- The user will see the `knowledge/` folder subdirectories (Credit, HR, etc.) populating in real-time.
- Check the Streamlit "Monitor" status to see the "Refinement" progress.

## Open Questions
- **{USER_QUESTION}**: Would you like me to proceed with processing **all 500 files** in parallel, or should we filter for a smaller sample to save API costs?
