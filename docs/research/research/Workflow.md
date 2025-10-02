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
We can start with **Phase 1** & **Phase 2** in parallel — one team handles data ingestion & processing, while another develops static/dynamic analysis wrappers so we can seed initial LLM fine-tuning in **Phase 4** as early as possible.


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





```markdown


# 3.1 Cross-Phase Integration Requirements

## JSON Schema Standards (Immediate Implementation)
All phases must adhere to unified data contracts to prevent integration delays:

### Findings Schema
```json
{
  "finding_id": "string (UUID)",
  "swc_id": "string (SWC-XXX format)",
  "severity": "enum [Critical, Major, Medium, Minor, Informational]",
  "tool_name": "string",
  "tool_version": "string",
  "file_path": "string",
  "line_span": {"start": "int", "end": "int"},
  "function_name": "string",
  "bytecode_offset": "int (optional)",
  "description": "string",
  "reproduction_steps": "string",
  "proof_of_concept": "string (optional)",
  "exploit_complexity": "enum [Low, Medium, High]",
  "confidence": "float [0.0-1.0]",
  "sanitizer_present": "boolean",
  "recommendations": "array[string]",
  "timestamp": "ISO 8601"
}
```

## Interim Severity Calibration (Phase 3 Stopgap)

Until full CVSS-inspired scoring is implemented, we can use this classification:

| Severity        | Description                         | Examples                                                       |
|-----------------|-------------------------------------|----------------------------------------------------------------|
| **Critical**    | Direct fund loss, contract takeover | Reentrancy with fund drain, arbitrary code execution           |
| **Major**       | Service disruption, governance bypass | DoS attacks, flash loan governance manipulation               |
| **Medium**      | Logic errors, privilege escalation  | Access control flaws, incorrect state transitions              |
| **Minor**       | Best practice violations            | Missing input validation, inefficient patterns                 |
| **Informational** | Code quality issues               | Style violations, unused variables                             |

**Mapping Rule:** Tools output severity → normalize to this ladder → store in findings schema.



# Phase 4: LLM & Prompt Management

## Core Technologies Required
- **LLM Stack:** HuggingFace Transformers (QLoRA/LoRA), tokenizer alignment with base model (LLaMA-class or GPT-compatible).
- **Retrieval:** FAISS/HNSW index or Vespa for hybrid BM25+dense retrieval; chunking with code-aware segmenters.
- **Prompt Ops:** Prompt template store, run metadata, automatic evaluation harness.
- **Fine-tuning Data:** Vulnerable–patched pairs, rationales, SWC exemplars, remediation patterns.
- **Safety & Guardrails:** Prompt injection and tool-use hardening, constrained decoding for code generation.

---

## Key Implementation Skills
- Supervised fine-tuning and instruction tuning for code tasks.
- RAG pipeline construction tailored to code (**AST/CFG-aware retrieval augmenters**).
- Self-reflection and prompt reranking loops (Reflexion/Re-ReST style).
- Patch synthesis with compiler/formatter integration and **minimal-diff constraints**.

---

## Implementation Guidelines

### Repository Layout

```text
llm_core/
prompts/        # templates, system messages, role-specific prompts
rag/            # indexers, retrievers, chunkers (code-aware)
finetune/       # training scripts, configs, data mappers
evaluators/     # unit tests, automatic metrics (exactness, compilability, tests pass)
policies/       # guardrails, content policies, tool-use constraints
```




### Data Pipeline
1. Ingest vulnerable–patched pairs; derive training triples:

```json
{ "vuln_code": "...", "findings_context": "...", "patch_rationale": "..." }
```

2. Enrich with:
- Detector outputs (from Phase 2)
- Scoring vectors (from Phase 3) as structured context
3. Normalize to **JSONL** for SFT.
4. Create retrieval passages:
- SWC patterns
- Secure idioms
- Diff snippets

---

### RAG Design
- **Pre-retrieval filters:** chain, language (Solidity/Vyper), SWC tags, library usage (OpenZeppelin).
- **Ranker:** shallow cross-encoder for **top-k** rerank of dense+BM25 candidates.
- **Context Packing:** interleave minimal code spans, SWC notes, and prior successful patches; cap tokens.

---

### Prompt Optimization Module
- Store trials with:
  - prompt_id
  - inputs
  - retrieved contexts
  - outputs
  - outcome metrics (compile, tests, fuzz pass)


- **Self-reflection:** summarize failures, hypothesize adjustments, generate prompt edits.
- **Rerank:** moving average of success metrics, decay stale prompts, quarantine unsafe patterns.

---

### Training Strategy
- **Stage 1:** SFT on curated pairs with rationales.
- **Stage 2:** Preference optimization (DPO/ORPO) using human- or rubric-based preferences:
- Smaller diffs
- Gas neutrality
- Explicit checks
- **Stage 3:** Light RL on environment feedback:
- Compiler success
- Unit tests
- Fuzz pass

---

### Inference & Tooling
- **Constrained generation:** grammar-guided decoding for Solidity, enforce minimal diffs and style.
- **Compile-time hooks:** solc compilation, Slither fast checks before surfacing.
- **Patch rationales:** require model to produce “why” with references to retrieved SWC guidance.

---

### Safety & Hallucination Mitigation
- Retrieval-only facts for security claims; flag low-retrieval-confidence outputs.
- Penalize unsupported API or language constructs for target compiler version.
- Run-time guardrails:
- Block `tx.origin` authentication
- Block unchecked low-level calls without checks

---

### Evaluation & KPIs
- **Metrics:**
- Patch acceptance rate (HITL)
- Compilability
- Unit/fuzz test pass rate
- Exploit resistance delta post-patch
- **Leaderboard:** track per-SWC performance, average diff size, gas impact.
- **Canary set:** unchanged across releases to monitor drift.

---

### Integration with Agents
- **PatchSuggesterAgent:** uses RAG + prompt templates specialized for patch diffs and rationales.
- **DetectionAgent:** provides structured findings and code spans to condition generation.
- **PatchVerificationAgent:** consumes rationale, runs toolchain, and feeds results back to Prompt Optimization.






# Phase 5: Multi-Agent Orchestration

## Core Technologies Required
- **Agent Frameworks:** Familiarity with conversational agent libraries (e.g., LangChain, Haystack).
- **Messaging & Eventing:** Use of lightweight message buses (e.g., RabbitMQ, Redis Streams) or actor frameworks (e.g., Ray, Akka).
- **Containerization:** Docker or Kubernetes for isolating agent processes.

## Key Implementation Skills
- Designing agent interfaces and contracts (communication protocols, input/output schemas).
- Implementing arbitration logic (leader election, quorum consensus algorithms).
- Building resilient event-driven pipelines with retry and back-pressure controls.

## Implementation Guidelines
- Define each agent’s API using **OpenAPI/gRPC**, with strict input validation (Protobuf/Pydantic schemas).
- Use a central orchestrator or workflow engine (e.g., **Temporal**, **Apache Airflow**) to sequence agent tasks and handle failures.
- Ensure **idempotent** agent operations and incorporate health-checks and metrics (**Prometheus** instrumentation).

---

# Phase 6: Explainability & Human-in-the-Loop (HITL)

## Core Technologies Required
- **Traceability Frameworks:** Tools for capturing execution traces (e.g., OpenTelemetry).
- **Visualization Libraries:** D3.js, Chart.js, or React-based graph components for rendering decision paths.
- **UI Frameworks:** React or Vue with component libraries (Ant Design, Material UI).

## Key Implementation Skills
- Instrumenting code to emit structured logs and trace spans.
- Designing interactive diff and annotation interfaces for code review.
- Implementing feedback loops that capture user decisions and update model datasets.

## Implementation Guidelines
- Expose an **“Explain”** endpoint returning: tool logs, concise reasoning summaries (no raw chain-of-thought), and patch rationale.
- Build a review dashboard with side-by-side code diffs, inline comments, and confidence indicators.
- Persist user feedback in a versioned store; trigger downstream retraining or prompt-ranking updates.

---

### Phase 7: Reinforcement Learning Loop

## Core Technologies Required
- **RL Libraries:** RLlib or Stable Baselines 3 for PPO implementations.
- **Data Stores:** High-throughput storage for replay buffers (e.g., Redis, Cassandra).
- **Experiment Tracking:** Tools like Weights & Biases or MLflow.

## Key Implementation Skills
- Defining reward functions that balance security (exploit resistance) and functionality (test-pass rate).
- Configuring replay buffer sampling strategies and on-policy vs. off-policy trade-offs.
- Monitoring training stability and performance regressions.

## Implementation Guidelines
- Encode each patch suggestion trial as an **RL episode**; capture state (vulnerabilities detected), action (patch applied), and reward.
- Use modular trainers: separate environments for static analysis validation vs. dynamic fuzzing feedback.
- Automate hyperparameter sweeps and log results for comparison; incorporate early stopping based on reward convergence.

---

### Phase 8: API, CI/CD & Deployment

## Core Technologies Required
- **Web Frameworks:** FastAPI or gRPC for high-throughput endpoints.
- **CI/CD Platforms:** GitHub Actions, GitLab CI, or Jenkins with container build capabilities.
- **Deployment Orchestration:** Docker Compose for local stacks; Helm/Kustomize for Kubernetes clusters.

## Key Implementation Skills
- Designing RESTful/gRPC interfaces with authentication (OAuth 2.0, API keys) and rate limiting.
- Writing comprehensive test suites: unit, integration (using test containers), and end-to-end (via Postman/Newman).
- Implementing blue-green or canary deployments with automated rollback.

## Implementation Guidelines
- Define **OpenAPI** contracts covering all services; auto-generate client SDKs.
- Integrate linting (**flake8**, **eslint**), type checks (**mypy**, **TypeScript**), and security analysis (**Bandit**, **Snyk**) into CI pipelines.
- Publish Docker images to a secure registry; tag by **semantic versioning**.
- Automate benchmarks against **OpenAuditBenchmark** on every merge to `main`; fail builds on regressions.

---






