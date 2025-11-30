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
declare -a FILES_TO_FIX
while IFS= read -r -d '' file; do
    if [[ -n "$(tail -c 1 "$file" | tr -d '\n')" ]]; then
        echo "" >> "$file"
        FILES_TO_FIX+=("$file")
    fi
done < <(find src/ tests/ -type f \( -name "*.py" -o -name "*.sh" \) -print0)

if [ ${#FILES_TO_FIX[@]} -gt 0 ]; then
    echo "The following files did not end with a newline and were fixed:"
    printf '%s\n' "${FILES_TO_FIX[@]}"
fi

echo "Code formatted successfully!"
