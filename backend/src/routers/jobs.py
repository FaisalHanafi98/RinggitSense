"""
RinggitSense - Job routes for async pipeline management.

POST /jobs — trigger a pipeline run, returns job_id immediately
GET /jobs/{job_id} — poll for status, current stage, errors
GET /jobs — list recent pipeline runs for the current user
"""
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database import get_db
from src.models.data_source import DataSource
from src.models.pipeline_run import PipelineRun
from src.models.user import User
from src.schemas.base import APIResponse, PaginationMeta
from src.schemas.pipeline import PipelineRunCreate, PipelineRunResponse
from src.services.pipeline import create_pipeline_run, run_pipeline

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=APIResponse[PipelineRunResponse], status_code=status.HTTP_202_ACCEPTED)
async def trigger_pipeline(
    body: PipelineRunCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger an async agent pipeline run for an uploaded statement.

    Returns immediately with a job_id. Poll GET /jobs/{job_id} for status.
    """
    # Verify the data source belongs to this user
    source_result = await db.execute(
        select(DataSource).where(
            DataSource.id == body.source_id,
            DataSource.user_id == user.id,
        )
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found or does not belong to you",
        )

    # Check for existing active pipeline run on this source
    existing = await db.execute(
        select(PipelineRun).where(
            PipelineRun.source_id == body.source_id,
            PipelineRun.status.in_(["pending", "running"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pipeline is already running for this data source",
        )

    run = await create_pipeline_run(db, user.id, body.source_id)
    background_tasks.add_task(run_pipeline, run.id)

    return APIResponse(data=PipelineRunResponse.model_validate(run))


@router.get("/{job_id}", response_model=APIResponse[PipelineRunResponse])
async def get_pipeline_status(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the status of a pipeline run."""
    result = await db.execute(
        select(PipelineRun).where(
            PipelineRun.id == job_id,
            PipelineRun.user_id == user.id,
        )
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pipeline run not found",
        )

    return APIResponse(data=PipelineRunResponse.model_validate(run))


@router.get("", response_model=APIResponse[dict])
async def list_pipeline_runs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List pipeline runs for the current user, newest first."""
    count_result = await db.execute(
        select(func.count()).select_from(PipelineRun).where(
            PipelineRun.user_id == user.id
        )
    )
    total = count_result.scalar_one()

    offset = (page - 1) * limit
    rows = await db.execute(
        select(PipelineRun)
        .where(PipelineRun.user_id == user.id)
        .order_by(PipelineRun.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    runs = rows.scalars().all()

    return APIResponse(
        data={
            "runs": [PipelineRunResponse.model_validate(r) for r in runs],
            "pagination": PaginationMeta.from_query(page=page, limit=limit, total=total),
        }
    )
