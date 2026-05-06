"""
RinggitSense - User routes
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.base import APIResponse
from src.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=APIResponse[UserResponse])
async def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    """Get the current authenticated user's profile."""
    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
    )


@router.put("/me", response_model=APIResponse[UserResponse])
async def update_current_user_profile(
    update_data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current authenticated user's profile."""
    # Update only provided fields
    if update_data.name is not None:
        user.name = update_data.name
    if update_data.monthly_income is not None:
        user.monthly_income = update_data.monthly_income
    if update_data.currency is not None:
        user.currency = update_data.currency
    if update_data.settings is not None:
        user.settings = {**user.settings, **update_data.settings}

    await db.commit()
    await db.refresh(user)

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the current user's account and all associated data."""
    await db.delete(user)
    await db.commit()
