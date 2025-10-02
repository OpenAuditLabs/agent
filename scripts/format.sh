#!/bin/bash
set -e

echo "Formatting Python code with black..."
black src/ tests/

echo "Sorting imports with isort..."
isort src/ tests/

echo "Fixing trailing whitespace and line endings..."
# Remove trailing whitespace
find src/ tests/ -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} +

echo "Code formatted successfully!"
