# Workflow Document: Agentic AI Smart Contract Security Framework

## 1. Purpose
This document defines the formal workflow for building the **Agentic AI** framework for smart contract vulnerability detection, scoring, patch generation, and mitigation.  
It covers what needs to be developed, how it should be implemented, verification processes, and integration procedures.

---

## 2. Scope
The workflow applies to all engineering teams involved in:

- **Core Auditing Engine** (static/dynamic analysis, scoring, patch validation)
- **Agentic AI Layer** (LLM orchestration, multi-agent coordination)
- **Training & Reinforcement Learning**
- **Human-in-the-Loop & Explainability Modules**
- **API/Frontend Integration**
- **Benchmarking & Deployment**

---

## 3. Phased Development Plan
# Phase 1: Dataset & Knowledge Base Initialization (Placeholder)

## Objective
Reserve this phase slot for the finalized dataset acquisition and preprocessing workflow without prescribing concrete steps.

## Overview
This placeholder outlines the eventual role of Phase 1, signaling where complete details on sourcing, normalizing, and annotating smart contract data will be inserted once the **Dataset Workflow Document** is finalized.

---

## Placeholder Elements

### Data Categories
- Source code repositories (e.g., verified smart contracts)
- Bytecode artifacts
- Vulnerability metadata and labels
- Benchmark cases (paired vulnerable/patched examples)

### Artifact Types
- Abstract Syntax Trees (AST)
- Control Flow Graphs (CFG)
- Opcode sequences

### Output Convention
- **Directory:** `/data/processed/`
- **Metadata fields:** placeholder keys (e.g., `vuln_class`, `source_id`, `swc_tag`)

---

## Guidance for Downstream Phases
- Refer to these high-level placeholders in schema definitions, API contracts, and test stubs.
- Avoid hard coding parsers or tool versions; rely on mock interfaces until the detailed workflow is published.
- Use **"TBD by Dataset Workflow Document"** in code comments where actual ingestion or labeling logic will reside.

---

## Temporary Exit Criteria
- Completion and approval of the dedicated Dataset Workflow Document by the data engineering and security teams.
- Replacement of this section with detailed procedures, tooling choices, and verification steps under controlled versioning.

---

## Next Action
Proceed with Phases 2 and beyond using stubbed dataset interfaces; revisit Phase 1 once the comprehensive Dataset Workflow Document is ready for integration.


### **Phase 2: Static & Dynamic Analysis Integration**
**Objective:** Wrap existing analyzers and fuzzers into unified Python modules.

**Tasks:**
- **Static Analysis Subsystem** (`audit-engine/static_analysis/`):
  - Integrate Mythril, Slither, and Manticore via CLI/Python API wrappers.
- **Dynamic Analysis Subsystem** (`audit-engine/dynamic_fuzzing/`):
  - Integrate Echidna for property-based fuzzing.
  - Add **AdversarialFuzz** for edge-case adversarial input generation.

**Output:**
- Standardized JSON vulnerability reports with severity, location, and reproduction steps.

**How to do it:**
- Create Python adapter classes for each tool.
- Define a unified JSON schema for outputs using **Pydantic** models.
- Test integration with sample contracts from SWC registry.

---

### **Phase 3: Vulnerability Scoring Engine**
**Objective:** Quantify detected vulnerabilities by severity.

**Tasks:**
- Implement **CVSS-inspired** scoring adapted for smart contract risk factors:
  - Financial impact
  - Exploit complexity
  - On-chain damage potential
- Accept multiple detection tool outputs and combine them into a weighted score.
- Expose scoring as callable module for LLM agents.

**How to do it:**
- Define scoring formula in `audit-engine/scoring_engine/`.
- Use historical exploit datasets to calibrate weight factors.

---

### **Phase 4: LLM & Prompt Management**
**Objective:** Train/fine-tune LLM for interpretation, scoring, and patch suggestion.

**Tasks:**
- Fine-tune **LLaMA/GPT** model on vulnerable–patched code pairs.
- Implement retrieval-augmented generation (**RAG**) to bring in SWC-specific patterns.
- Build a **Prompt Optimization Module** that:
  - Stores historical prompts & results.
  - Applies self-reflection after each run.
  - Reranks prompt effectiveness.

**How to do it:**
- Use **HuggingFace transformers** for local fine-tuning.
- Implement **FAISS** or **Vespa** for retrieval index.
- Follow **Reflexion/Re-ReST** style loop for self-improvement.

---

### **Phase 5: Multi-Agent Orchestration**
**Objective:** Distribute specialized tasks across coordinated agents.

**Agent Roles:**
- `DetectionAgent` → Runs static/dynamic scans and interprets results.
- `ExploitSimulationAgent` → Attempts to exploit vulnerabilities (red-team).
- `PatchSuggesterAgent` → Generates secure patches.
- `PatchVerificationAgent` → Validates patch safety and deployability.

**Consensus:**
- Use scoring consensus across agents before surfacing results.

**How to do it:**
- Implement agents in `agentic_core/agents/`, each with isolated tool access.
- Use event/message-passing for agent communication.
- Define arbitration logic to resolve disagreements.

---

### **Phase 6: Explainability & Human-in-the-Loop (HITL)**
**Objective:** Build trust and enable developer oversight.

**Tasks:**
- **Explainability Module:**
  - Trace tool outputs, model reasoning, and decision paths.
  - Generate counterfactual explanations.
- **Interactive Review UI:**
  - Side-by-side diff of original and patched code.
  - Confidence scores & validation status.
- **Feedback Integration:**
  - Approved/rejected patches update LLM fine-tuning dataset.
  - Update trust scores for prompts and agents.

**How to do it:**
- Backend: `/services/api/` endpoints for serving explanations.
- Frontend: React/Vue-based UI in `/services/frontend/`.

---

### **Phase 7: Reinforcement Learning Loop**
**Objective:** Continuously improve agent performance.

**Tasks:**
- Define reward functions based on:
  - Patch acceptance rate.
  - Test suite pass rate.
  - Exploit resistance post-patch.
- Train agents with **PPO** using a replay buffer of past cases.

**How to do it:**
- Store replay buffer in `/training/replay_buffer/`.
- Use **RLlib** or custom PPO trainer in `/training/rl_loop/`.

---

### **Phase 8: API, CI/CD & Deployment**
**Objective:** Provide production-ready, reproducible services.

**Tasks:**
- **API Layer:** REST/gRPC endpoints for IDE & CI/CD integration.
- **CI/CD:**
  - Linting, unit/integration tests.
  - Auto-benchmarking against OpenAuditBenchmark.
- **Deployment:**
  - Docker-based packaging for reproducibility.
  - Staging → Production rollout.

**How to do it:**
- Use **FastAPI** for API services.
- **GitHub Actions/GitLab CI** for automated testing.
- **Docker Compose** to orchestrate multi-container setup.

---

## 4. Verification & Acceptance Criteria
- **Unit Test Coverage:** ≥ 85% for all core modules.
- **Benchmark Scores:** Must outperform baseline tools (**AuditGPT**, **Smartify**) in **F1 ≥ +5%**.
- **HITL Feedback Adoption:** Approved patch rate ≥ 80%.
- **Post-Deployment Defense:** Detect and mitigate ≥ 90% of red-team simulated attacks.

---

## 5. Deliverables Per Phase
- Scripts, configs, adapters, and documentation.
- Fine-tuned model weights and prompts archive.
- API & frontend interface for developer use.
- Dockerized deployment package.
- Benchmark report comparing with latest research tools.

---

✅ **Next Step Recommendation:**  
Start with **Phase 1** & **Phase 2** in parallel — one team handles data ingestion & processing, while another develops static/dynamic analysis wrappers so you can seed initial LLM fine-tuning in **Phase 4** as early as possible.


# Technical Requirements and Implementation Guidelines by Phase

---

## Phase 1: Dataset & Knowledge Base Initialization (Placeholder)

### Core Technologies Required
- **Data Management:** Understanding of data versioning systems (DVC, Git LFS) for large dataset management.
- **Metadata Standards:** Knowledge of vulnerability classification frameworks (CWE, SWC Registry).
- **Storage Solutions:** Experience with structured data storage (PostgreSQL, MongoDB) for metadata management.
- **Data Quality:** Familiarity with data validation and cleaning methodologies for blockchain code analysis.

### Key Implementation Skills
- Dataset curation and preprocessing pipeline design.
- Vulnerability taxonomy and labeling system development.
- Data governance and quality assurance protocols.

---

## Phase 2: Static & Dynamic Analysis Integration

### Essential Technologies

#### Static Analysis Tools
- **Slither:** Python-based framework.  
  Installation:  
  ```bash
  pip install slither-analyzer
