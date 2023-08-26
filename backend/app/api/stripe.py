import uuid
from typing import Annotated

import sqlalchemy as sa
import stripe
from fastapi import Depends, Header, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from loguru import logger
from opentelemetry import trace
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app import deps, models
from app.auth.jwt import (
    StripeCheckoutTokenResponse,
    create_stripe_checkout_token,
    decode_stripe_checkout_token,
)
from app.settings import settings

tracer = trace.get_tracer(__name__)


router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)

if settings.DEV:
    stripe.api_key = (
        "sk_test_51NiAqMCJiKhdlW4v8mN2P5MYa5J2k1eN13ZFz1dkQtzBU0qVeizSzJu4q9sKD"
        "rehkkmCWDBj8XGxGDoRThw1Y9u800nVEK7yGv"
    )
    WEBHOOK_SECRET = (
        "whsec_01e4952cdd27084be9bfb6c96e419741a91aad888a5b1bf84668c598ef66b61a"
    )
else:
    stripe.api_key = settings.STRIPE_API_KEY
    WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

# TODO the frontend host and port should be read from env variable
CHECKOUT_SUCCESS_URL = (
    "http://localhost:3000?success=true&session_id={CHECKOUT_SESSION_ID}"
)
CHECKOUT_CANCEL_URL = "http://localhost:3000?canceled=true"


class PortalResponse(BaseModel):
    url: str


@router.get("/checkout-token", response_model=StripeCheckoutTokenResponse)
async def create_checkout_token(
    user: Annotated[uuid.UUID, Depends(deps.get_current_active_user)],
    # expire_seconds: Annotated[int, Query(ge=60)] = 60 * 60 * 24 * 7,
):
    # Stripe allows up to 200 tokens, and for long expire times, we could go over that limit.
    # None gives 172 tokens. 1 week gives 195 tokens! I (Jonny) think it's ok to not expire these.
    token = create_stripe_checkout_token(user_id=user.id, expire_seconds=None)
    return StripeCheckoutTokenResponse(token=token)


@router.get("/create-portal-session", response_model=PortalResponse, status_code=200)
async def customer_portal(
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    if user.stripe_customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="User must first make a payment before viewing their payment portal",
        )
    portal_session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url="http://localhost:3000",  # TODO (Jonny): replace with some env variables or something
    )
    return PortalResponse(url=portal_session.url)


@router.post("/webhook")
async def webhook_received(
    request: Request,
    stripe_signature: Annotated[str, Header()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    # This actually MUST use the raw bytes as an argument.
    # https://github.com/stripe/stripe-node/issues/1254
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=WEBHOOK_SECRET,
        )
    except ValueError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    logger.info(f"Received Stripe event: {event.type}. EventID: {event.id}")
    match event.type:
        case "checkout.session.completed":
            checkout_session: stripe.checkout.Session = event.data.object
            logger.info(
                f"Checkout session ID: {checkout_session.id}. Customer ID: {checkout_session.customer}"
            )

            token: str = event.data.object.client_reference_id
            checkout_token = decode_stripe_checkout_token(token=token)
            user_id = checkout_token.user_id

            if not (user := await db.get(models.User, user_id)):
                detail = f"Invalid stripe-access token. User does not exist: {user_id}"
                logger.error(detail)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=detail
                )

            if not user.stripe_customer_id:
                logger.info("Creating customer for user.")
                user.stripe_customer_id = checkout_session.customer

            sub = stripe.Subscription.retrieve(
                checkout_session.subscription, expand=["items.data.price.product"]
            )

            subscription_model = models.Subscription(
                user_id=user_id,
                amount=int(sub.plan.amount),
                currency=sub.plan.currency,
                interval=sub.plan.interval,
                stripe_customer_id=checkout_session.customer,
                stripe_subscription_id=sub.stripe_id,
                stripe_status=sub.status,
                stripe_created=int(sub.created),
                stripe_current_period_start=int(sub.current_period_start),
                stripe_current_period_end=int(sub.current_period_end),
                stripe_quantity=int(sub.quantity),
                stripe_price_id=sub["items"].data[0].price.id,
                stripe_price_lookup_key=sub["items"].data[0].price.lookup_key,
                stripe_product_id=sub["items"].data[0].price.product.id,
                stripe_product_name=sub["items"].data[0].price.product.name,
                stripe_cancel_at_period_end=sub.cancel_at_period_end,
            )
            db.add(subscription_model)
            await db.commit()

        case "customer.subscription.updated":
            raw_sub: stripe.Subscription = event.data.object
            logger.info(f"Subscription ID: {raw_sub.id}")
            sub = stripe.Subscription.retrieve(
                id=raw_sub.id, expand=["items.data.price.product"]
            )
            values = dict(
                amount=int(sub.plan.amount),
                currency=sub.plan.currency,
                interval=sub.plan.interval,
                stripe_customer_id=sub.customer,
                stripe_subscription_id=sub.stripe_id,
                stripe_status=sub.status,
                stripe_created=int(sub.created),
                stripe_current_period_start=int(sub.current_period_start),
                stripe_current_period_end=int(sub.current_period_end),
                stripe_quantity=int(sub.quantity),
                stripe_price_id=sub["items"].data[0].price.id,
                stripe_price_lookup_key=sub["items"].data[0].price.lookup_key,
                stripe_product_id=sub["items"].data[0].price.product.id,
                stripe_product_name=sub["items"].data[0].price.product.name,
                stripe_cancel_at_period_end=sub.cancel_at_period_end,
            )
            await db.execute(
                sa.update(models.Subscription)
                .where(models.Subscription.stripe_subscription_id == sub.id)
                .values(**values)
            )
            await db.commit()

        case "customer.subscription.deleted":
            sub: stripe.Subscription = event.data.object
            logger.info(f"Subscription ID: {sub.id}")
            await db.execute(
                sa.update(models.Subscription)
                .where(models.Subscription.stripe_subscription_id == sub.id)
                .values(stripe_status=sub.status)
            )
            await db.commit()

    return JSONResponse(content="", status_code=status.HTTP_200_OK)
