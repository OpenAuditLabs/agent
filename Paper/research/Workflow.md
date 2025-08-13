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

### **Phase 1: Data Acquisition & Preprocessing**
**Objective:** Establish robust, clean, and structured datasets for training and evaluation.

**Tasks:**
- **Data Sources:**
  - Download Solidity contracts from SWC Registry, Etherscan verified source, and public exploits repositories.
  - Include paired vulnerable–patched contracts from **OpenAuditBenchmark**.
- **Preprocessing:**
  - Normalize code style and structure.
  - Extract **AST** (Abstract Syntax Tree), **CFG** (Control Flow Graph), opcode sequences.
  - Label vulnerability types and severity.
- **Output:**
  - Store in `/data/processed/` with metadata (vulnerability class, source ID, CWE/SWC tag).

**How to do it:**
- Use `solidity-parser` for AST extraction.
- Convert bytecode to CFG using **Slither** or custom parser.
- Implement Python scripts for dataset ingestion and labeling.

---

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
