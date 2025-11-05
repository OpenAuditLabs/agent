from typing import Optional

from pydantic import BaseModel, Field


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
