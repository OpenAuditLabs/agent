#!/bin/bash
set -e

pytest_k_arg=""
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -k)
            if [ -n "$2" ]; then
                pytest_k_arg="-k "$2""
                shift # past argument
            else
                echo "Error: -k option requires an argument."
                exit 1
            fi
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift # past argument or value
done

echo "Running unit tests..."
source .venv/bin/activate
pytest tests/unit/ -v --cov=src/oal_agent --cov-report=term-missing $pytest_k_arg

echo "Running integration tests..."
pytest tests/integration/ -v $pytest_k_arg

echo "Running e2e tests..."
pytest tests/e2e/ -v $pytest_k_arg

echo "All tests passed!"
