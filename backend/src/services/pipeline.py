"""
RinggitSense - Async agent pipeline service.

Runs the 6-agent pipeline (AG-01 → AG-06) as a background job.
Upload returns immediately; frontend polls GET /jobs/{id} for status.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_maker
from src.models.pipeline_run import PipelineRun
from src.models.transaction import Transaction

logger = logging.getLogger(__name__)

# Semaphore limits concurrent Claude API calls across all pipeline runs
_claude_semaphore = asyncio.Semaphore(3)

# Agent stage definitions — order matters
PIPELINE_STAGES = [
    ("AG-01", "categorizer"),
    ("AG-02", "debt_detector"),
    ("AG-03", "pattern_analyzer"),
    ("AG-04", "predictor"),
    ("AG-05", "query"),
    ("AG-06", "advisor"),
]


def get_claude_semaphore() -> asyncio.Semaphore:
    """Expose semaphore for testing."""
    return _claude_semaphore


async def create_pipeline_run(
    db: AsyncSession,
    user_id: uuid.UUID,
    source_id: uuid.UUID,
) -> PipelineRun:
    """Create a new pipeline run record."""
    run = PipelineRun(
        id=uuid.uuid4(),
        user_id=user_id,
        source_id=source_id,
        status="pending",
        total_stages=len(PIPELINE_STAGES),
        stage_results={},
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def run_pipeline(run_id: uuid.UUID) -> None:
    """Execute the agent pipeline in the background.

    Each stage acquires the semaphore before calling Claude.
    On failure, the pipeline stops and records the error — it does NOT
    continue through remaining stages (Sen2Nal lesson: C3).
    """
    async with async_session_maker() as db:
        # Load the pipeline run
        result = await db.execute(
            select(PipelineRun).where(PipelineRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            logger.error("Pipeline run %s not found", run_id)
            return

        # Mark as running
        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        await db.commit()

        # Load transactions for this source
        txn_result = await db.execute(
            select(Transaction).where(
                Transaction.user_id == run.user_id,
                Transaction.source_id == run.source_id,
            )
        )
        transactions = txn_result.scalars().all()

        if not transactions:
            run.status = "completed"
            run.completed_at = datetime.now(timezone.utc)
            run.error_message = "No transactions found for this source"
            await db.commit()
            return

        stage_results = run.stage_results or {}

        for i, (agent_id, stage_name) in enumerate(PIPELINE_STAGES):
            run.current_stage = stage_name
            await db.commit()

            try:
                async with _claude_semaphore:
                    stage_result = await _execute_stage(
                        agent_id, stage_name, transactions, stage_results, db
                    )

                stage_results[stage_name] = stage_result
                run.stages_completed = i + 1
                run.stage_results = stage_results
                await db.commit()

            except Exception as e:
                logger.exception(
                    "Pipeline %s failed at stage %s: %s", run_id, stage_name, e
                )
                run.status = "failed"
                run.error_message = str(e)
                run.error_stage = stage_name
                run.completed_at = datetime.now(timezone.utc)
                run.stage_results = stage_results
                await db.commit()
                return

        # All stages completed
        run.status = "completed"
        run.current_stage = None
        run.completed_at = datetime.now(timezone.utc)
        await db.commit()


async def _execute_stage(
    agent_id: str,
    stage_name: str,
    transactions: list[Transaction],
    prior_results: dict,
    db: AsyncSession,
) -> dict:
    """Execute a single pipeline stage.

    AG-01 (Categorizer) and AG-02 (Debt Detector) are implemented.
    Other stages return a placeholder indicating they're not yet available —
    this lets the pipeline run end-to-end without failing on unimplemented agents.
    """
    if agent_id == "AG-01":
        return await _run_categorizer(transactions, db)

    if agent_id == "AG-02":
        return await _run_debt_detector(transactions, prior_results, db)

    if agent_id == "AG-03":
        return await _run_pattern_analyzer(transactions, prior_results)

    # Stub for unimplemented agents — returns metadata, doesn't fail
    return {
        "status": "skipped",
        "reason": f"{agent_id} ({stage_name}) not yet implemented",
    }


async def _run_categorizer(
    transactions: list[Transaction],
    db: AsyncSession,
) -> dict:
    """Run AG-01 Categorizer on uncategorized transactions."""
    from src.agents.categorizer import CategorizerAgent

    uncategorized = [t for t in transactions if t.category is None]
    if not uncategorized:
        return {"status": "skipped", "reason": "all transactions already categorized"}

    agent = CategorizerAgent()
    categorized_count = 0
    errors = []

    for txn in uncategorized:
        try:
            result = agent.categorize(
                description=txn.description,
                amount=float(txn.amount),
                source="upload",
                date=str(txn.transaction_date),
            )
            txn.category = result.category.value
            txn.category_confidence = result.confidence
            txn.subcategory = result.subcategory
            txn.merchant_name = result.merchant_name
            categorized_count += 1
        except Exception as e:
            errors.append({"transaction_id": str(txn.id), "error": str(e)})

    await db.commit()
    return {
        "status": "completed",
        "categorized": categorized_count,
        "errors": errors,
        "total": len(uncategorized),
    }


async def _run_pattern_analyzer(
    transactions: list[Transaction],
    prior_results: dict,
) -> dict:
    """Run AG-03 Pattern Analyzer on categorized transactions.

    AG-03 runs AFTER AG-01 and AG-02. It receives the full transaction list
    plus AG-02's debt signals so it can correlate BNPL usage with spending
    spikes. Transactions are serialized to dicts before being passed to the
    agent — the agent works on plain data, not ORM objects.
    """
    from src.agents.pattern_analyzer import PatternAnalyzerAgent

    if not transactions:
        return {"status": "skipped", "reason": "no transactions to analyze"}

    txn_dicts = [
        {
            "id": str(t.id),
            "date": str(t.transaction_date),
            "description": t.description,
            "amount": float(t.amount),
            "category": t.category,
            "subcategory": getattr(t, "subcategory", None),
        }
        for t in transactions
    ]

    debt_signals = prior_results.get("debt_detector")

    agent = PatternAnalyzerAgent()
    result = agent.analyze(
        transactions=txn_dicts,
        period="available",
        debt_signals=debt_signals,
    )

    return {
        "status": "completed",
        "pattern_count": len(result.patterns),
        "hidden_cost_total": result.hidden_cost_total,
        "summary": result.summary,
        "patterns": [
            {
                "type": p.type.value,
                "name": p.name,
                "impact": p.impact,
                "confidence": p.confidence,
            }
            for p in result.patterns
        ],
    }


async def _run_debt_detector(
    transactions: list[Transaction],
    prior_results: dict,
    db: AsyncSession,
) -> dict:
    """Run AG-02 Debt Detector on categorized transactions.

    AG-02 runs AFTER AG-01. It examines all transactions (not just
    debt-categorized ones) because informal debts (HUTANG) may appear
    as transfers rather than explicit debt payments.
    """
    from src.agents.debt_detector import DebtDetectorAgent

    if not transactions:
        return {"status": "skipped", "reason": "no transactions to analyze"}

    agent = DebtDetectorAgent()
    detected_count = 0
    errors = []

    for txn in transactions:
        try:
            result = agent.detect(
                description=txn.description,
                amount=float(txn.amount),
                source="upload",
                is_recurring=False,
            )
            if result.is_debt_related:
                detected_count += 1
                txn.is_debt_related = True
                txn.debt_tier = result.debt_tier.value if result.debt_tier else None
        except Exception as e:
            errors.append({"transaction_id": str(txn.id), "error": str(e)})

    await db.commit()
    return {
        "status": "completed",
        "detected": detected_count,
        "errors": errors,
        "total": len(transactions),
    }
