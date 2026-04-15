# 📝 RAG-Destroyer: Development & Stability Log

This document serves as a formal record of the system's evolution, technical incidents, and the industrial-grade solutions implemented to ensure long-term stability and scalability.

---

## 🏛️ Milestone 1: Industrialization & Resilience
**Date:** 2026-04-15
**Goal:** Transition from a functional prototype to a professional enterprise management engine.

### 🚩 Incident: Silent Crashes & API Congestion
- **Problem**: During high-frequency testing, the Gemini API would frequently hit rate limits (429 errors), causing the system to stop responding without clear feedback to the user.
- **Root Cause**: The original search workers used too many parallel bot instances (4-8), exceeding API quota quickly.
- **Solution**:
    1. **Industrial Sweet Spot**: Standardized the search pool to **2 parallel bots** for maximum reliability without hitting hard limits.
    2. **Safety-Cut (Circuit Breaker)**: Implemented a failure counter in `Orchestrator.py`. If the AI fails twice consecutively, the system enters "Cool-down Mode" to protect the API quota and notifies the admin.

### 🚩 Incident: Data Privacy & GitHub Leakage
- **Problem**: The original codebase was tightly coupled with a private Obsidian Vault and Google Drive folders.
- **Solution**: 
    1. **Silo-Native RBAC**: Implemented logic that respects the OS-level folder permissions.
    2. **GitHub Policy**: Enforced a strict `.gitignore` for the `knowledge/` and `.obsidian/` folders to ensure ZERO private data is ever uploaded to public repositories.

---

## 🏛️ Milestone 2: PnP (Plug & Play) & Multi-LLM Support
**Date:** 2026-04-15
**Goal:** Making the project portable and vendor-agnostic for global users.

### 🚩 Incident: The "Hardcoded Path" Bottleneck
- **Problem**: The code relied on absolute paths like `/Users/tong/...`, making it impossible for other users (from GitHub) to run the app without manually editing Python files.
- **Solution**:
    1. **Dynamic Root Resolution**: Implemented a `ROOT_PATH` constant in `Utils.py` that automatically calculates the project's location on any machine.
    2. **Knowledge Valve**: Created a UI section in `app.py` for dynamic path selection.

### 🚩 Incident: Vendor Lock-in (Gemini Only)
- **Problem**: While Gemini 2.5 is excellent, industrial users required diversity (OpenAI, Anthropic) for redundancy.
- **Solution**: 
    1. **Strategy Pattern**: Created a unified `BaseProvider` class in `core/LLMProviders.py`.
    2. **Multi-Provider Factory**: Decoupled the Orchestrator from the Gemini SDK, allowing it to swap backends on the fly via the UI.

---

## 📈 Current Progress Summary
- [x] **Core Brain**: Zero-Vector-DB Subset Theory perfected.
- [x] **Resilience**: Watchdog & Safety-Cut active.
- [x] **UI**: Financial Org Simulation Dashboard complete.
- [x] **PnP**: Fully portable for GitHub deployment.
- [x] **Multi-LLM**: Google, OpenAI, and Anthropic supported.

---
**Maintained by:** RAG-Destroyer Industrial AI Advisor
**Last Update:** 2026-04-15
