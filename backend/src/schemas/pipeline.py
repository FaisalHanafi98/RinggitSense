"""
RinggitSense - Pipeline job schemas for API request/response.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PipelineRunResponse(BaseModel):
    """Pipeline run status in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    source_id: UUID
    status: str
    current_stage: Optional[str] = None
    stages_completed: int
    total_stages: int
    error_message: Optional[str] = None
    error_stage: Optional[str] = None
    stage_results: Optional[dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class PipelineRunCreate(BaseModel):
    """Request body for triggering a pipeline run."""
    source_id: UUID
