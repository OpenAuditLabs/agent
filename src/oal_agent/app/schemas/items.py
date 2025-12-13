from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ItemCreate(BaseModel):
    name: str = Field(
        ..., min_length=3, max_length=50, description="The name of the item"
    )
    description: Optional[str] = Field(
        None,
        min_length=10,
        max_length=500,
        description="A detailed description of the item",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Smartwatch X1",
                    "description": "A cutting-edge smartwatch with health tracking and notification features.",
                }
            ]
        }
    }


class Item(ItemCreate):
    id: int = Field(..., description="The unique identifier of the item")
    is_deleted: bool = Field(
        False, description="True if the item is soft-deleted, False otherwise"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Smartwatch X1",
                    "description": "A cutting-edge smartwatch with health tracking and notification features.",
                    "is_deleted": False,
                }
            ]
        }
    }


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=3, max_length=50, description="The new name of the item"
    )
    description: Optional[str] = Field(
        None,
        min_length=10,
        max_length=500,\        description="The new detailed description of the item",
    )
    is_deleted: Optional[bool] = Field(
        None, description="Set to True to soft-delete the item, False to restore"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Smartwatch X1 Pro",
                    "description": "Updated model with enhanced battery life and new sports modes.",
                    "is_deleted": True,
                }
            ]
        }
    }

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ItemUpdate":
        if self.name is None and self.description is None and self.is_deleted is None:
            raise ValueError(
                "At least one of 'name', 'description', or 'is_deleted' must be provided."
            )
        return self
