# 🌳 Digital Bank - Family Tree Org Chart (V2)

This chart represents the 5-layer hierarchical structure of the bank, optimized for **RAG-Destroyer** access control and department-level filing.

## 📊 The Banking Family Tree

```mermaid
graph TD
    %% Level 1: The Crown
    CEO["👑 CEO<br/>Chief Executive Officer<br/>(Master Access)"]
    
    %% Level 2: The Roots (C-Suite)
    CFO["📊 CFO<br/>Chief Financial Officer"]
    COO["⚙️ COO<br/>Chief Operating Officer"]
    CTO["💻 CTO<br/>Chief Technology Officer"]
    CHRO["👥 CHRO<br/>Chief HR Officer"]
    CRO["⚖️ CRO<br/>Chief Risk Officer"]

    %% Level 3: The Branches (VPs / Heads)
    VP_CRL["🏦 VP of Credit & Lending"]
    VP_OPS["🏪 VP of Branch Operations"]
    VP_ITD["💻 VP of Digital Engineering"]
    VP_HRA["📝 Head of People & Culture"]
    VP_RSK["⚖️ Director of Compliance"]

    %% Level 4: The Twigs (Managers)
    MG_CRL["Senior Loan Manager"]
    MG_OPS["Area Branch Manager"]
    MG_ITD["System Architect"]
    MG_HRA["HR Operations Manager"]
    MG_RSK["Internal Audit Manager"]

    %% Level 5: The Leaves (Execution)
    ST_CRL["Loan Processing Officer"]
    ST_OPS["Senior Teller Officer"]
    ST_ITD["DevOps Engineer"]
    ST_HRA["Senior Recruiter"]
    ST_RSK["Compliance Officer"]

    %% Connections
    CEO --> CFO
    CEO --> COO
    CEO --> CTO
    CEO --> CHRO
    CEO --> CRO

    CFO --- VP_CRL
    COO --- VP_OPS
    CTO --- VP_ITD
    CHRO --- VP_HRA
    CRO --- VP_RSK

    VP_CRL --- MG_CRL
    VP_OPS --- MG_OPS
    VP_ITD --- MG_ITD
    VP_HRA --- MG_HRA
    VP_RSK --- MG_RSK

    MG_CRL --- ST_CRL
    MG_OPS --- ST_OPS
    MG_ITD --- ST_ITD
    MG_HRA --- ST_HRA
    MG_RSK --- ST_RSK

    %% Styling
    style CEO fill:#FFD700,stroke:#333,stroke-width:3px,color:#000
    style CFO,COO,CTO,CHRO,CRO fill:#f9f,stroke:#333,stroke-width:2px
    style VP_CRL,VP_OPS,VP_ITD,VP_HRA,VP_RSK fill:#bbf,stroke:#333
    style MG_CRL,MG_OPS,MG_ITD,MG_HRA,MG_RSK fill:#dfd,stroke:#333
    style ST_CRL,ST_OPS,ST_ITD,ST_HRA,ST_RSK fill:#fff,stroke:#333
```

## 📜 Hierarchy Levels Definition

| Level | Title | Responsibility |
| :--- | :--- | :--- |
| **L1** | **CEO** | Total Bank Oversight & Strategic Mandates |
| **L2** | **C-Suite** | Departmental P&L and Multi-Subset Authority |
| **L3** | **VP / Head** | Tactical Deployment & Subset Quality Control |
| **L4** | **Manager** | Day-to-day Supervision & Ingestion Review |
| **L5** | **Officer** | Direct Data Generation & Customer Interaction |

---
*📍 **Location:** This visual tree is synchronized with `config/org_structure.json` and governs the internal search workers.*
