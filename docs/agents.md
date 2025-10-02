# Agents

## Overview

This document describes the different agents in the system and their responsibilities.

## Agent Types

### Coordinator Agent
Routes analysis tasks to the appropriate specialized agents based on the contract type and analysis requirements.

### Static Agent
Performs static analysis using tools like Slither and other static analyzers.

### Dynamic Agent
Performs dynamic analysis through symbolic execution and fuzzing.

### ML Agent
Uses machine learning models to detect patterns and anomalies in smart contracts.

## Agent Communication

Agents communicate through a message queue system and report results to a centralized results sink.
