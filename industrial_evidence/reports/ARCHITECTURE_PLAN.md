# ARCHITECTURE_PLAN.md - RAG-Destroyer (Zero-Vector-DB)

## Goal
Establish **"RAG-Destroyer" (Zero-Vector-DB Architecture)**: A deterministic LLM-OS knowledge management system utilizing **The Subset Theory** and **Silo-Native Access Control** without the overhead of traditional Vector Databases.

## User Review Required
> [!IMPORTANT]
> **Parallel Search Architecture**: The system utilizes 3-4 simultaneous "Search Bots" to scan for authorized documents based on AI-generated keywords, ensuring speed and comprehensive coverage.
> **Access Control (Silo Isolation)**: Data is logically and physically partitioned by department. User access is strictly scoped to authorized subsets; cross-departmental searching is blocked at the kernel level.
> **The Subset Theory**: Instead of semantic drift, we use deterministic intersection logic on results from multi-threaded worker bots to identify the "Pristine Subset" of documents before AI synthesis.

### [Industrial Resilience & Operations Layer]
- **Optimized Parallel Swarm**: Configured for **2 keywords simultaneously** to maximize API stability and minimize latency jitter.
- **Safety-Cut (Circuit Breaker)**: Embedded in the Orchestrator to automatically halt processing after 2 consecutive fatal errors, preventing resource waste.
- **Identity-Aware Audit**: Dual-channel alerts (Console + LINE Notify) for critical system events.
- **Zombie Cleanup**: Persistent PID-based process monitoring ensures zero ghost background monitors.

## Active System Architecture

### [Core Components]

#### [Orchestrator.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/Orchestrator.py)
The Main Controller: Receives queries -> Generates Multilingual Keywords -> Dispatches Parallel Bots -> Isolated Subset Calculation -> Final Global Expert Synthesis.

#### [SearchWorker.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/SearchWorker.py)
Micro-Code Bots: Executed in parallel to search for files based on keyword lists within department constraints (Powered by high-speed JSON Cache).

#### [Refinery.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/Refinery.py)
Raw Data Processing: Ingests files from `raw_data/`, uses Gemini for content refining, smart naming, and vault registration with full metadata (Doc ID).

#### [VaultWarden.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/VaultWarden.py)
Vault Management: Audits all documents, generates the Master Index (.md) and Search Cache (.json) for sub-millisecond retrieval.

#### [Exporter.py](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/core/Exporter.py)
Export Engine: Supports high-fidelity conversion from Markdown to Docx/PDF for global corporate reporting.

### [Security & Silo-Native RBAC Layer]

#### Identity-to-Silo Mapping
Driven by `org_structure.json`, enforcing rigorous data isolation (LLM OS standards):
- **Registry Check**: Every request is validated against the User Database to determine Role and Department permissions.
- **Search Kernel Enforcement**: Bots are physically restricted to scanning only authorized directories. AI never processes unauthorized data.
- **Compliance Ready**: Ensures cross-departmental isolation, preventing data leakage across organizational silos.

### [System Configuration]

#### [.env](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/config/.env)
Global configuration for API Keys, Model selection, and local/cloud storage paths.

#### [requirements.txt](file:///Users/tong/Documents/MyClaw/RAG-Destroyer/requirements.txt)
Core Dependencies: `google-genai`, `python-frontmatter`, `python-dotenv`, `fpdf2`.

## Verification Plan
### Automated Testing
- `python core/VaultWarden.py` (Tests index and cache generation)
- `python core/Orchestrator.py` (Tests the end-to-end AI synthesis pipeline)

### Manual Verification
- Verify "Silo Isolation" by logging in with different departmental roles.
- Test multilingual queries (Thai/English) to ensure consistent global synthesis quality.

## Future Roadmap
### 1. Hardware-Level Identity
- Integration with NFC/RFID card readers for physical employee card-based silo unlocking.
- Mobile Biometrics (FaceID/TouchID) support for secure session authorization.

### 2. Context-Aware Security
- Geo-fencing support: High-security silo access restricted to specific office locations and trusted networks.

### 3. Mobile Ecosystem
- Mobile-first web interface and dedicated app support for on-the-go "Global Guru" consulting.

