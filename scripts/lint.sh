#!/bin/bash
set -e

source .venv/bin/activate

echo "Running black..."
black --check src/ tests/


echo "Running isort..."
isort --check-only src/ tests/

echo "Running flake8..."
flake8 --max-line-length=88 --ignore=E203,E704,E501,E302,W503 src/ tests/

echo "All linting checks passed!"
