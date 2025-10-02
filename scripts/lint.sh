#!/bin/bash
set -e

echo "Running black..."
black --check src/ tests/

echo "Running isort..."
isort --check-only src/ tests/

echo "Running flake8..."
flake8 src/ tests/

echo "Running mypy..."
mypy src/

echo "All linting checks passed!"
