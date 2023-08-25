from typing import Annotated

import sqlalchemy as sa
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models, schemas
from app.deps.users import Plan, UserAndPlan

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"],
    responses={404: {"description": "Not found"}},
)


# Doesn't actually delete anything O.o
@router.get("/me", response_model=schemas.Subscription)
async def get_my_subscriptions(
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user_and_plan: Annotated[UserAndPlan, Depends(deps.get_free_or_paying_user)],
):
    user = user_and_plan.user
    if user_and_plan.plan == Plan.free:
        raise HTTPException(
            status_code=400, detail="Free plan users do not yet have a customer portal"
        )
    subs = await db.scalar(
        sa.select(models.Subscription).where(models.Subscription.user_id == user.id)
    )
    return subs.first()
