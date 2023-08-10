from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, List, Optional

import sqlalchemy as sa
import stripe
from fastapi import (
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from stripe.error import StripeError

from app import models, schemas
from app.deps.users import get_current_active_user
from app.deps.db import get_async_session
#from app.models import Subscription 
from app.settings import settings

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)


# class WebHookData(BaseModel):
#     data: dict
#     type: str


# @router.post("/", response_model=schemas.Clone)
# async def create(
#     obj: schemas.CloneCreate,
#     db: Annotated[AsyncSession, Depends(get_async_session)],
#     user: Annotated[models.User, Depends(current_active_user)],
# ):
#     clone = models.Clone(**obj.dict(), user_id=user.id)
#     db.add(clone)
#     await db.commit()
#     await db.refresh(clone)
#     return clone


# @router.post("/create-product")
# async def create_product(request: Request):
#     content_type = request.headers.get("Content-Type")
#     if content_type is None:
#         return "No Content-Type provided."
#     elif content_type == "application/json":
#         try:
#             product_info = await request.json()
#             print(type(product_info))
#             product = stripe.Product.create(
#                 api_key=settings.STRIPE_KEY,
#                 name=product_info["name"],
#                 description=product_info["description"],
#             )
#             print("success")
#             return {"status_code": status.HTTP_200_OK, "detail": product}
#         except Exception as e:
#             return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}
#     else:
#         print("Content-Type not supported.")


# @router.post("/create-account-link")
# async def create_account_link(
#     request: Request, user: Annotated[models.User, Depends(current_active_user)]
# ):
#     name = user.name
#     id = user.id
#     email = user.email

#     user_url = "http://localhost:3000/" + name if name else None

#     client_id = settings.STRIPE_CONNECT_CLIENT_ID
#     redirect_uri = "http://localhost:8000/stripe/link/callback"

#     stripe_oauth_url = (
#         "https://connect.stripe.com/express/oauth/authorize?response_type=code"
#     )

#     metadata_list = [
#         {"client_id": client_id},
#         {"scope": "read_write"},
#         # {"state": ""},
#         {"redirect_uri": redirect_uri},
#         {"stripe_user[email]": request.email},
#         {"stripe_user[url]": user_url},
#     ]

#     for metadata in metadata_list:
#         metadata_key = list(metadata.keys())[0]
#         metadata_val = list(metadata.values())[0]
#         stripe_oauth_url = stripe_oauth_url + "&" + metadata_key + "=" + metadata_val

#     return {"url": stripe_oauth_url}


# @router.post("/link/callback")
# async def create_account_callback(url_handle: str, code: str):
#     if url_handle is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL handle"
#         )

#     if code is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code"
#         )

#     response = stripe.OAuth.token(grant_type="authorization_code", code=code)

#     connected_account_id = response["stripe_user_id"]
#     access_token = response["access_token"]
#     # TODO: save connected_account_id and access_token to profile
#     return {"message": "Stripe account successfully connected"}


# @router.post("/create-customer")
# async def create_customer(email: str, name: str):
#     ## TODO: auth?
#     try:
#         customer = stripe.Customer.create(email=email, name=name)
#         return {"status_code": status.HTTP_200_OK, "detail": customer}
#     except Exception as e:
#         return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


## TODO:
## stripe edge cases - double pay, upgrading plans, changing cards
## email not there if discord auth 
@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[models.User, Depends(get_current_active_user)],
):
    
    stripe_customer_id = user.stripe_customer_id
    stripe.api_key = settings.STRIPE_API_KEY

    if stripe_customer_id is None:
        customer = stripe.Customer.create(email=user.email)
        stripe_customer_id = customer.id
        user.stripe_customer_id = stripe_customer_id
        await db.commit()
    else:
        stripe_customer_id = user.stripe_customer_id
    
    content_type = request.headers.get("Content-Type")
    if content_type is None:
        return "No Content-Type provided."
    elif content_type == "application/json":
        try:
            product_info = await request.json()
        except Exception as e:
            print("Invalid JSON data: " + str(e))
    else:
        print("Content-Type not supported.")
    try:
        price_id = product_info["priceId"]
        checkout_session = stripe.checkout.Session.create(
            api_key=settings.STRIPE_API_KEY,
            customer=stripe_customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items = [{
                "price": price_id,
                "quantity": 1,
            }],
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )
        
        # TODO: edit - add subscription to db
        # subscription = models.Subscription(
        #     customer_id=checkout_session["customer"],
        #     subscription_id=checkout_session.id,
        #     user_id=user.id,
        #     stripe_status=checkout_session.status,
        #     stripe_created=checkout_session.created,
        #     stripe_current_period_start=checkout_session.subscription.current_period_start,
        #     stripe_current_period_end=checkout_session.subscription.current_period_end,
        #     stripe_cancel_at_period_end=checkout_session.subscription.cancel_at_period_end,
        #     stripe_canceled_at=checkout_session.subscription.canceled_at,
        # )
        # await db.add(subscription)
        # await db.commit()

        return {"status_code": status.HTTP_200_OK, "detail": checkout_session}
    except Exception as e:
        return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


# @router.post("/create-subscription")
# async def create_subscription(
#     request: Request,
#     db: Annotated[AsyncSession, Depends(get_async_session)],
#     user: Annotated[models.User, Depends(current_active_user)],
# ):
#     content_type = request.headers.get("Content-Type")
#     if content_type is None:
#         return "No Content-Type provided."
#     elif content_type == "application/json":
#         try:
#             subscription_info = await request.json()
#             print(subscription_info)
#         except Exception as e:
#             print("Invalid JSON data: " + str(e))
#     else:
#         print("Content-Type not supported.")
#     try:
#         subscription = stripe.Subscription.create(
#             api_key=settings.STRIPE_KEY,
#             customer=subscription_info["customer"],
#             items=subscription_info["items"],
#         )
#         subscription = models.Subscription(
#             user_id=user.id,
#             subscription_id=subscription["id"],
#             customer_id=subscription["customer"],
#             stripe_status=subscription["status"],
#             stripe_created=subscription["created"],
#             stripe_current_period_start=subscription["current_period_start"],
#             stripe_current_period_end=subscription["current_period_end"],
#             stripe_cancel_at_period_end=subscription["cancel_at_period_end"],
#             stripe_canceled_at=subscription["canceled_at"],
#         )
#         await db.add(subscription)
#         await db.commit()

#         return {"status_code": status.HTTP_200_OK, "detail": subscription}
#     except Exception as e:
#         return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


# @router.post("/create-payout")
# async def create_payout(
#     stripe_connect_account_id: str,
#     user: Annotated[models.User, Depends(current_active_user)],
# ):
#     amount = 0.0  # TODO: get total payout balance
#     TAKE_RATE = 0.2
#     amount = amount * TAKE_RATE

#     try:
#         transfer = stripe.Transfer.create(
#             api_key=settings.STRIPE_KEY,
#             amount=amount,
#             currency="usd",
#             destination=stripe_connect_account_id,
#         )

#         print("success")
#         # TODO: add payouts to db

#         return {"status_code": status.HTTP_200_OK, "detail": transfer}
#     except Exception as e:
#         return {"status_code": status.HTTP_403_FORBIDDEN, "detail": str(e)}


# ## Usage based


# @router.post("/create-usage-record")
# async def create_usage_record(
#     request: Request,
#     db: Annotated[AsyncSession, Depends(get_async_session)],
#     user: Annotated[models.User, Depends(current_active_user)],
# ):
#     content_type = request.headers.get("Content-Type")
#     if content_type is None:
#         raise HTTPException(status_code=400, detail="No Content-Type provided.")
#     elif content_type == "application/json":
#         try:
#             usage_record_info = await request.json()
#         except Exception as e:
#             raise HTTPException(status_code=400, detail="Invalid JSON data: " + str(e))
#     else:
#         raise HTTPException(status_code=400, detail="Content-Type not supported.")

#     try:
#         usage_record = stripe.SubscriptionItem.create_usage_record(
#             subscription_id=usage_record_info["subscription_item_id"],
#             quantity=usage_record_info["quantity"],
#             timestamp=usage_record_info.get("timestamp"),
#         )
#         usage_record = models.UsageRecord(
#             user_id=user.id,
#             subscription_item_id=usage_record["subscription_item"],
#             quantity=usage_record["quantity"],
#             timestamp=usage_record["timestamp"],
#         )
#         await db.add(usage_record)
#         await db.commit()

#         return JSONResponse(
#             status_code=200, content={"status_code": 200, "detail": usage_record}
#         )
#     except StripeError as e:
#         raise HTTPException(status_code=403, detail=str(e))


# @router.get("/usage-total/{subscription_item_id}")
# async def get_usage_total(
#     subscription_item_id: str,
#     db: Annotated[AsyncSession, Depends(get_async_session)],
#     user: Annotated[models.User, Depends(current_active_user)],
# ):
#     try:
#         subscription_item = stripe.SubscriptionItem.retrieve(subscription_item_id)
#         subscription_item_id = subscription_item["id"]
#         usage_records = await db.scalars(
#             sa.select(models.UsageRecord)
#             .where(models.UsageRecord.user_id == user.id)
#             .where(models.UsageRecord.subscription_item_id == subscription_item_id)
#         )
#         # sum up all the quantity
#         total = 0
#         for usage_record in usage_records:
#             total += usage_record.quantity

#         return JSONResponse(
#             status_code=200,
#             content={"status_code": 200, "total": total},
#         )
#     except StripeError as e:
#         raise HTTPException(status_code=403, detail=str(e))


# @router.post("/invoice-customer")
# async def invoice_customer(request: Request):
#     content_type = request.headers.get("Content-Type")
#     if content_type is None:
#         raise HTTPException(status_code=400, detail="No Content-Type provided.")
#     elif content_type == "application/json":
#         try:
#             invoice_info = await request.json()
#         except Exception as e:
#             raise HTTPException(status_code=400, detail="Invalid JSON data: " + str(e))
#     else:
#         raise HTTPException(status_code=400, detail="Content-Type not supported.")

#     try:
#         invoice = stripe.Invoice.create(
#             customer=invoice_info["customer"], auto_advance=True
#         )
#         # TODO: process invoice

#         return JSONResponse(
#             status_code=200, content={"status_code": 200, "detail": invoice}
#         )
#     except StripeError as e:
#         raise HTTPException(status_code=403, detail=str(e))


# @router.get("/get-invoice/{invoice_id}")
# async def get_invoice(invoice_id: str):
#     try:
#         invoice = stripe.Invoice.retrieve(invoice_id)
#         return JSONResponse(
#             status_code=200, content={"status_code": 200, "detail": invoice}
#         )
#     except StripeError as e:
#         raise HTTPException(status_code=403, detail=str(e))


# @router.post("/webhook")
# def handle_webhook(
#     request_data: WebHookData, stripe_signature: Optional[str] = Header(None)
# ):
#     webhook_secret = settings.STRIPE_WEBHOOK_SECRET

#     if webhook_secret:
#         signature = stripe_signature
#         try:
#             event = stripe.Webhook.construct_event(
#                 payload=request_data, sig_header=signature, secret=webhook_secret
#             )
#             data = event["data"]
#         except Exception as e:
#             return e
#         event_type = event["type"]
#     else:
#         data = request_data["data"]
#         event_type = request_data["type"]
#     data_object = data["object"]

#     print("webhook event " + event_type)
#     print("webhook data = " + data_object)

#     if event_type == "checkout.session.completed":
#         print("TODO: handle checkout.session.completed event")
#     elif event_type == "payment_intent.succeeded":
#         print("TODO: handle payment_intent.succeeded event")
#     elif event_type == "payment_intent.payment_failed":
#         print("TODO: handle payment_intent.payment_failed event")

#     return {"status_code": status.HTTP_200_OK, "detail": ""}
