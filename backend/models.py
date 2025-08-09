from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class DrawingIdea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(..., min_length=1, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_submitted: bool = Field(default=True)

class DrawingIdeaCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=200)

class DrawingIdeaResponse(BaseModel):
    id: str
    text: str
    created_at: datetime
    user_submitted: bool