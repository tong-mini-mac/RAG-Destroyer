# 🏛️ RAG-Destroyer: Zero-Vector-DB Architecture SOP v1.0

This Standard Operating Procedure (SOP) defines the operational guidelines for the **RAG-Destroyer** knowledge management system, utilizing the **Zero-Vector-DB** architecture to function as an "Industrial Digital Librarian" powered by **The Subset Theory**.

---

## 🏛️ 1. Knowledge Ingestion Process
The Librarian serves as a gatekeeper to ensure data integrity before it enters the vault (Deterministic Ingestion).

### Step 1.1: Registration (The Registrar Bot)
*   **Context Analysis**: The AI analyzes content to determine the appropriate "Shelf" (Silo) based on the **Silo-Native RBAC** architecture defined in `config/org_structure.json`.
*   **Knowledge Coding**: The Librarian assigns a unique Document ID (Doc ID) for seamless retrieval and future cross-referencing.
*   **Intelligence Tagging**: Relevant tags and cross-departmental links are injected to ensure knowledge mobility across specialized silos.

---

## 🗃️ 2. Shelf Maintenance
Maintaining structural integrity and organization within the library is handled by the **Vault Warden**.

### Step 2.1: Master Indexing
*   The Warden continuously updates the `_MASTER_INDEX.md` file, providing executives with a high-level overview of all organizational knowledge assets.

---

## 📖 3. Expert Synthesis Process
When a knowledge request is received, the Librarian executes the following synthesis pipeline:

### Step 3.1: Intent Interpretation
*   The **Orchestrator** acts as a Senior Digital Librarian, interpreting the user's strategic intent and identifying the specific silos required to build an accurate "Subset".

### Step 3.2: Expert Report Synthesis
*   The Librarian gathers data from multiple sources to generate a comprehensive **"Executive Knowledge Report"** that directly addresses the query, eliminating the need for users to manually browse raw files.

---

## 🛡️ 4. Data Governance Standards
*   **Operational Staff**: Access is strictly limited to the document silos directly related to their current role and department.
*   **Executive Leadership**: The Librarian grants authorized cross-silo access to "Global Knowledge Vaults" based on established organizational credentials (CEO, CFO, CTO, etc.).

---

## 🧪 5. Demo Audit & Continuous Improvement
In this Industrial Demo edition, a two-tier audit system is implemented for performance optimization:
*   **AI QC Judge**: Every response is evaluated by an autonomous AI Judge to ensure accuracy, tone, and the absence of hallucinations.
*   **Audit Dashboard**: Users can access real-time Accuracy and QC scores via the dashboard to analyze system performance and identify areas for code or prompt refinement.

---

## 🛡️ 6. GitHub & Privacy Policy
*   **GitHub Repository**: Contains the core logic, orchestration engine, and dashboard code only.
*   **Data Exclusion**: The `knowledge/` folder (Obsidian Vault) and internal organizational structures are strictly ignored by `.gitignore` to maintain 100% data privacy.

---
**Developed by:** RAG-Destroyer Industrial AI Team
**Version:** 1.1 (2026-04-15) - Industrial Demo Edition
