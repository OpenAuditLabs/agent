# Agents

## Overview

This document describes the different agents in the system and their responsibilities.

## Agent Types

### Coordinator Agent
Routes analysis tasks to the appropriate specialized agents based on the contract type and analysis requirements.

### Coordinator Agent Lifecycle

The `CoordinatorAgent` (defined in `src/oal_agent/agents/coordinator.py`) is responsible for orchestrating the analysis pipeline by receiving incoming tasks and routing them to the most suitable specialized agents (Static, Dynamic, ML Agents).

**Intended Sequence Steps:**

1.  **Task Ingestion:** The Coordinator Agent continuously monitors a task queue for new analysis requests.
2.  **Task Evaluation:** Upon receiving a task, the Coordinator evaluates its characteristics, such as contract type, requested analysis types, and priority.
3.  **Agent Selection:** Based on the evaluation, the Coordinator selects one or more appropriate specialized agents capable of performing the required analysis. This selection might involve considering agent availability, current load, and specific capabilities.
4.  **Task Dispatch:** The task is then dispatched to the selected specialized agent(s) via their respective input queues.
5.  **Result Monitoring (Future):** In a more advanced lifecycle, the Coordinator would also monitor the progress and results from the dispatched tasks, potentially handling retries or escalating issues.

**Configuration Knobs (Planned/Conceptual):**

While the current implementation in `src/oal_agent/agents/coordinator.py` is a placeholder with routing logic marked as `TODO`, future iterations would likely include the following configuration options:

*   **Routing Rules:** Define rules or policies for how tasks are mapped to specialized agents (e.g., "Solidity contracts go to Static Agent first," "High-priority tasks get preference").
*   **Agent Endpoints/Discovery:** Configuration for discovering and connecting to available specialized agents.
*   **Load Balancing Strategies:** Parameters to distribute tasks efficiently among multiple instances of the same specialized agent.
*   **Retry Mechanisms:** Configuration for how many times to retry a task if an agent fails, and with what backoff strategy.
*   **Task Prioritization:** Settings to influence how tasks are prioritized when multiple agents are available.

### Static Agent
Performs static analysis using tools like Slither and other static analyzers.

### Dynamic Agent
Performs dynamic analysis through symbolic execution and fuzzing.

### ML Agent
Uses machine learning models to detect patterns and anomalies in smart contracts.

## Agent Communication

Agents communicate through a message queue system and report results to a centralized results sink.
