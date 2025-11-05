from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ItemCreate(BaseModel):
    name: str = Field(..., description="The name of the item")
    description: Optional[str] = Field(
        None, description="A detailed description of the item"
    )


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The new name of the item")
    description: Optional[str] = Field(
        None, description="The new detailed description of the item"
    )

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "ItemUpdate":
        if self.name is None and self.description is None:
            raise ValueError(
                "At least one of 'name' or 'description' must be provided."
            )
        return self
