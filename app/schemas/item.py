import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CreateItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = None
    status: str = Field(default="active", pattern="^(active|inactive|draft)$")


class UpdateItemRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    status: str | None = Field(None, pattern="^(active|inactive|draft)$")


class ItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    category: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
