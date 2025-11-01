#!/bin/bash
set -e

echo "Running unit tests..."
source .venv/bin/activate
pytest tests/unit/ -v --cov=src/oal_agent --cov-report=term-missing

echo "Running integration tests..."
pytest tests/integration/ -v

echo "Running e2e tests..."
pytest tests/e2e/ -v

echo "All tests passed!"
