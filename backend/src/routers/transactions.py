"""
RinggitSense - Transaction routes (upload and list)
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database import get_db
from src.data_quality.transaction_validator import (
    DuplicateStatus,
    TransactionValidator,
)
from src.models.data_source import DataSource
from src.models.transaction import Transaction
from src.models.user import User
from src.parsers import get_parser, PARSER_REGISTRY
from src.parsers.base import ParsedTransaction
from src.schemas.base import APIResponse, PaginationMeta
from src.schemas.transaction import (
    DuplicateDetail,
    TransactionListResponse,
    TransactionResponse,
    UploadResponse,
    UploadValidationDetail,
)
from src.services.pipeline import create_pipeline_run, run_pipeline

router = APIRouter(prefix="/transactions", tags=["transactions"])

# L1: File validation constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {"csv"}
ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "text/plain",
    "application/vnd.ms-excel",
    "application/octet-stream",
}


def _validate_file(file: UploadFile) -> str:
    """L1: File-level validation. Returns the file extension."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: .{ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    return ext


@router.post(
    "/upload",
    response_model=APIResponse[UploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_transactions(
    file: UploadFile,
    bank: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a bank statement file and parse transactions.

    Flow: L1 file validation → parse → L2/L3 validation → L4 dedup → store.
    """
    # Validate bank code
    if bank.lower() not in PARSER_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported bank: {bank}. Supported: {', '.join(PARSER_REGISTRY.keys())}",
        )

    # L1: File validation
    _validate_file(file)

    # Read file content with size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    # Parse the statement
    parser = get_parser(bank)
    parse_result = parser.parse(content, filename=file.filename or "")

    if not parse_result.success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse statement: {'; '.join(parse_result.errors)}",
        )

    # L2 + L3: Validate parsed transactions
    validator = TransactionValidator()
    batch_result = validator.validate_batch(parse_result)

    # Collect validation errors for response
    validation_errors: list[UploadValidationDetail] = []
    for i, vr in enumerate(batch_result.results):
        if not vr.is_valid or vr.warnings:
            validation_errors.append(
                UploadValidationDetail(
                    row=i + 1,
                    errors=vr.errors,
                    warnings=vr.warnings,
                )
            )

    # Filter to only valid transactions
    valid_transactions = [
        txn
        for txn, vr in zip(parse_result.transactions, batch_result.results)
        if vr.is_valid
    ]

    # L4: Deduplication — load existing transactions for this user in the date range
    if valid_transactions:
        min_date = min(t.transaction_date for t in valid_transactions)
        max_date = max(t.transaction_date for t in valid_transactions)

        existing_rows = await db.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.transaction_date >= min_date,
                Transaction.transaction_date <= max_date,
            )
        )
        existing_db_txns = existing_rows.scalars().all()

        # Convert DB transactions to ParsedTransaction for the dedup checker
        existing_parsed: list[ParsedTransaction] = [
            ParsedTransaction(
                transaction_date=t.transaction_date,
                description=t.description,
                amount=t.amount,
                transaction_type="debit",  # type doesn't matter for dedup
            )
            for t in existing_db_txns
        ]
    else:
        existing_parsed = []

    # Run dedup and partition
    to_store: list[ParsedTransaction] = []
    duplicate_details: list[DuplicateDetail] = []
    duplicates_skipped = 0
    suspicious_count = 0

    for i, txn in enumerate(valid_transactions):
        dup_result = validator.check_duplicates(txn, existing_parsed)

        if dup_result.status == DuplicateStatus.DUPLICATE:
            duplicates_skipped += 1
            duplicate_details.append(
                DuplicateDetail(
                    row=i + 1,
                    description=txn.description,
                    amount=txn.amount,
                    transaction_date=txn.transaction_date,
                    status="DUPLICATE",
                    matching_description=dup_result.matching_description,
                )
            )
        elif dup_result.status == DuplicateStatus.SUSPICIOUS:
            suspicious_count += 1
            duplicate_details.append(
                DuplicateDetail(
                    row=i + 1,
                    description=txn.description,
                    amount=txn.amount,
                    transaction_date=txn.transaction_date,
                    status="SUSPICIOUS",
                    matching_description=dup_result.matching_description,
                )
            )
            # Still store suspicious — user can review later
            to_store.append(txn)
        else:
            to_store.append(txn)

    # Create DataSource record for this upload
    data_source = DataSource(
        id=uuid.uuid4(),
        user_id=user.id,
        source_type=bank.lower(),
        source_name=f"{parser.BANK_NAME} - {file.filename}",
        total_transactions=len(to_store),
        date_range_start=(
            min(t.transaction_date for t in to_store) if to_store else None
        ),
        date_range_end=(
            max(t.transaction_date for t in to_store) if to_store else None
        ),
    )
    db.add(data_source)

    # Store transactions
    for txn in to_store:
        db_txn = Transaction(
            id=uuid.uuid4(),
            user_id=user.id,
            source_id=data_source.id,
            transaction_date=txn.transaction_date,
            amount=txn.signed_amount,
            description=txn.description,
            original_description=txn.raw_data.get(
                next(
                    (k for k in txn.raw_data if "desc" in k.lower()),
                    "__none__",
                ),
                None,
            ),
            raw_data=txn.raw_data if txn.raw_data else None,
        )
        db.add(db_txn)

    await db.commit()
    await db.refresh(data_source)

    # Auto-trigger pipeline if transactions were stored
    pipeline_run = None
    if to_store:
        pipeline_run = await create_pipeline_run(db, user.id, data_source.id)
        background_tasks.add_task(run_pipeline, pipeline_run.id)

    return APIResponse(
        data=UploadResponse(
            source_id=data_source.id,
            bank_name=parser.BANK_NAME,
            total_parsed=parse_result.transaction_count,
            total_valid=batch_result.valid,
            total_invalid=batch_result.invalid,
            total_stored=len(to_store),
            duplicates_skipped=duplicates_skipped,
            suspicious_duplicates=suspicious_count,
            job_id=pipeline_run.id if pipeline_run else None,
            validation_errors=validation_errors,
            duplicate_details=duplicate_details,
            batch_warnings=batch_result.batch_warnings,
            parser_warnings=parse_result.warnings,
        )
    )


@router.get("", response_model=APIResponse[TransactionListResponse])
async def list_transactions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Start date (inclusive)"),
    date_to: Optional[date] = Query(None, description="End date (inclusive)"),
    source_id: Optional[uuid.UUID] = Query(None, description="Filter by data source"),
    search: Optional[str] = Query(None, min_length=1, max_length=200, description="Search description"),
):
    """List transactions for the current user with pagination and filtering."""
    # Base query scoped to user
    query = select(Transaction).where(Transaction.user_id == user.id)
    count_query = select(func.count()).select_from(Transaction).where(
        Transaction.user_id == user.id
    )

    # Apply filters
    if category:
        query = query.where(Transaction.category == category)
        count_query = count_query.where(Transaction.category == category)
    if date_from:
        query = query.where(Transaction.transaction_date >= date_from)
        count_query = count_query.where(Transaction.transaction_date >= date_from)
    if date_to:
        query = query.where(Transaction.transaction_date <= date_to)
        count_query = count_query.where(Transaction.transaction_date <= date_to)
    if source_id:
        query = query.where(Transaction.source_id == source_id)
        count_query = count_query.where(Transaction.source_id == source_id)
    if search:
        query = query.where(Transaction.description.ilike(f"%{search}%"))
        count_query = count_query.where(Transaction.description.ilike(f"%{search}%"))

    # Get total count
    total = (await db.execute(count_query)).scalar_one()

    # Paginate and order
    offset = (page - 1) * limit
    query = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit)
    rows = await db.execute(query)
    transactions = rows.scalars().all()

    return APIResponse(
        data=TransactionListResponse(
            transactions=[
                TransactionResponse.model_validate(t) for t in transactions
            ],
            pagination=PaginationMeta.from_query(page=page, limit=limit, total=total),
        )
    )
