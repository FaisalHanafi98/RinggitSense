"""
RinggitSense - Pipeline job schemas for API request/response.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PipelineRunResponse(BaseModel):
    """Pipeline run status in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    source_id: UUID
    status: str
    current_stage: str | None = None
    stages_completed: int
    total_stages: int
    error_message: str | None = None
    error_stage: str | None = None
    stage_results: dict | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class PipelineRunCreate(BaseModel):
    """Request body for triggering a pipeline run."""
    source_id: UUID
