from typing import Annotated, Optional, List, Dict, Any

from app import models, schemas
from app.auth.users import current_active_user
from app.db import get_async_session
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.routing import APIRouter
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.settings import settings
from pydantic import BaseModel
import stripe

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)


class WebHookData(BaseModel):
    data: dict
    type: str


@router.post("/", response_model=schemas.Clone)
async def create(
    obj: schemas.CloneCreate,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(current_active_user)],
):
    clone = models.Clone(**obj.dict(), user_id=user.id)
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return clone


@router.post("/create-product")
async def create_product(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type is None:
        return "No Content-Type provided."
    elif content_type == "application/json":
        try:
            product_info = await request.json()
            print(type(product_info))
            product = stripe.Product.create(
                api_key=settings.STRIPE_KEY,
                name=product_info["name"],
                description=product_info["description"],
            )
            print("success")
            return {"status_code": status.HTTP_200_OK, "detail": product}
        except Exception as e:
            return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}
    else:
        print("Content-Type not supported.")


@router.post("/create-customer")
async def create_customer(email: str, name: str):
    ## TODO: auth?
    try:
        customer = stripe.Customer.create(email=email, name=name)
        return {"status_code": status.HTTP_200_OK, "detail": customer}
    except Exception as e:
        return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type is None:
        return "No Content-Type provided."
    elif content_type == "application/json":
        try:
            product_info = await request.json()
            print(product_info)
            # items = make_line_items(product_info)

        except Exception as e:
            print("Invalid JSON data: " + str(e))
    else:
        print("Content-Type not supported.")
    try:
        checkout_session = stripe.checkout.Session.create(
            api_key=settings.STRIPE_KEY,
            payment_method_types=["card"],
            line_items=product_info["items"],
            mode="payment",
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )
        print("success")
        # TODO: add orders to db

        return {"status_code": status.HTTP_200_OK, "detail": checkout_session}
    except Exception as e:
        return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


@router.post("/create-subscription")
async def create_subscription(request: Request):
    content_type = request.headers.get("Content-Type")
    if content_type is None:
        return "No Content-Type provided."
    elif content_type == "application/json":
        try:
            subscription_info = await request.json()
            print(subscription_info)
        except Exception as e:
            print("Invalid JSON data: " + str(e))
    else:
        print("Content-Type not supported.")
    try:
        subscription = stripe.Subscription.create(
            api_key=settings.STRIPE_KEY,
            customer=subscription_info["customer"],
            items=subscription_info["items"],
        )
        print("success")
        # TODO: add subscriptions to db

        return {"status_code": status.HTTP_200_OK, "detail": subscription}
    except Exception as e:
        return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


@router.post("/webhook")
def handle_webhook(
    request_data: WebHookData, stripe_signature: Optional[str] = Header(None)
):
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if webhook_secret:
        signature = stripe_signature
        try:
            event = stripe.Webhook.construct_event(
                payload=request_data, sig_header=signature, secret=webhook_secret
            )
            data = event["data"]
        except Exception as e:
            return e
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]
    data_object = data["object"]

    print("webhook event " + event_type)
    print("webhook data = " + data_object)

    if event_type == "checkout.session.completed":
        print("TODO: handle checkout.session.completed event")
    elif event_type == "payment_intent.succeeded":
        print("TODO: handle payment_intent.succeeded event")
    elif event_type == "payment_intent.payment_failed":
        print("TODO: handle payment_intent.payment_failed event")

    return {"status_code": status.HTTP_200_OK, "detail": ""}
