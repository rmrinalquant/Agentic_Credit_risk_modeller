import os, json
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict



class Step(BaseModel):
    tool_name: str = Field(..., description="tool id or name (e.g., check_duplicates)")
    rationale: str
    inputs: dict = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")

class ActionPlan(BaseModel):
    query: str
    intent: str
    steps: List[Step]
    expected_outputs: Optional[List[str]] = None
    confidence: float = Field(..., ge=0, le=1)
    model_config = ConfigDict(extra="allow")