from typing import Optional, List
from pydantic import BaseModel, Field


class ExperimentRunRequest(BaseModel):
    model: str = Field(..., description="Ollama model tag, or 'demo' for Demo Mode")
    condition: str = Field(..., description="memory | personality | values | goals | model | progressive")
    transformation_percentage: int = Field(..., ge=0, le=100)
    trial_count: int = Field(5, ge=1, le=50)
    blind_condition: bool = False
    random_seed: Optional[int] = None
    question_set: Optional[List[str]] = None  # question ids; defaults to full bank


class ParsedIdentityResponse(BaseModel):
    same_entity: Optional[bool] = None
    identity_score: Optional[float] = None
    confidence: Optional[float] = None
    primary_identity_property: Optional[str] = None
    reason: Optional[str] = None
    parse_failed: bool = False
    raw_response: str = ""


class ExperimentSummary(BaseModel):
    id: str
    condition: str
    transformation_percentage: int
    model: str
    trial_count: int
    blind_condition: bool
    is_demo: bool
    status: str
    created_at: str
    identity_score_mean: Optional[float] = None
    confidence_mean: Optional[float] = None
