#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add the project root to the sys.path
sys.path.append(str(Path(__file__).parent.parent))

from src.oal_agent.app.schemas.items import ItemCreate, ItemUpdate
from src.oal_agent.app.schemas.jobs import PaginationParams, JobRequest, JobResponse

SCHEMA_DIR = Path(__file__).parent.parent / "data" / "schemas"
SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

def generate_schema(model, filename):
    schema = model.model_json_schema()
    if model == ItemUpdate:
        schema["x-validation-note"] = "At least one of 'name' or 'description' must be provided."
    with open(SCHEMA_DIR / filename, "w") as f:
        json.dump(schema, f, indent=2)

if __name__ == "__main__":
    # Items schemas
    generate_schema(ItemCreate, "item_create.json")
    generate_schema(ItemUpdate, "item_update.json")

    # Jobs schemas
    generate_schema(PaginationParams, "pagination_params.json")
    generate_schema(JobRequest, "job_request.json")
    generate_schema(JobResponse, "job_response.json")

    print(f"Generated JSON schemas in {SCHEMA_DIR}")