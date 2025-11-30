#!/bin/bash
set -e

echo "Formatting Python code with black..."
black src/ tests/

echo "Sorting imports with isort..."
isort src/ tests/

echo "Fixing trailing whitespace and line endings..."
# Remove trailing whitespace
find src/ tests/ -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} +

echo "Ensuring all files end with a newline..."
# Find files that do not end with a newline and add one
FILES_TO_FIX=$(find src/ tests/ -type f \( -name "*.py" -o -name "*.sh" \) -exec sh -c 'test -n "$(tail -c 1 "{}" | tr -d "\n")"' _ {} \;)
if [ -n "$FILES_TO_FIX" ]; then
    echo "The following files did not end with a newline and were fixed:"
    echo "$FILES_TO_FIX"
    echo "$FILES_TO_FIX" | xargs -r -d '\n' -I {} sh -c 'echo >> "{}"'
fi

echo "Code formatted successfully!"
