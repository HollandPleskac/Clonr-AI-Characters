from fastapi.routing import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Request, Header, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from app import models, schemas, deps
from app.settings import settings
from pydantic import BaseModel
from loguru import logger
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
import sqlalchemy as sa
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


if settings.DEV:
    stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
else:
    stripe.api_key = settings.STRIPE_API_KEY

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
    responses={404: {"description": "Not found"}},
)

if settings.DEV:
    WEBHOOK_SECRET = (
        "whsec_12345"  # TODO (Jonny): this should proll be an env variable or sum shit
    )
else:
    WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
CHECKOUT_SUCCESS_URL = (
    f"http://{settings.HOST}:{settings.PORT}"
    "?success=true&session_id={CHECKOUT_SESSION_ID}"
)
CHECKOUT_CANCEL_URL = f"http://{settings.HOST}:{settings.PORT}?canceled=true"


# TODO (Jonny): figure out the schema for data here
class WebHookData(BaseModel):
    data: dict
    type: str


class ProductCreate(BaseModel):
    name: str
    description: str


@router.post("/create-product", dependencies=[Depends(deps.get_superuser)])
async def create_product(
    product_create: ProductCreate, content_type: Annotated(str, Header())
):
    # IDk what this is for, but put it here in case it's needed
    # prices = stripe.Price.list(
    #     lookup_keys=[request.form["lookup_key"]], expand=["data.product"]
    # )
    if content_type != "application/json":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content type must be application/json",
        )
    try:
        product = stripe.Product.create(
            api_key=settings.STRIPE_KEY, **product_create.model_dump()
        )
        return jsonable_encoder(product)  # TODO (Jonny): find the output schema here
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


class ProductInfo(BaseModel):
    price_id: str


# TODO:
# stripe edge cases - double pay, upgrading plans, changing cards
# email not there if discord auth
@router.post("/create-checkout-session")
async def create_checkout_session(
    product_info: ProductInfo,
    content_type: Annotated(str, Header()),
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
):
    if content_type != "application/json":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content type must be application/json",
        )

    if user.stripe_customer_id is None:
        with tracer.start_as_current_span("Create_stripe_customer"):
            logger.info(f"Creating a Stripe customer for user: {user.id}")
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
            await db.commit()

    try:
        line_items = [dict(price=product_info.price_id, quantity=1)]
        checkout_session = stripe.checkout.Session.create(
            api_key=settings.STRIPE_API_KEY,
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=line_items,
            success_url=CHECKOUT_SUCCESS_URL,
            cancel_url=CHECKOUT_CANCEL_URL,
        )

        subscription = models.Subscription(
            customer_id=checkout_session["customer"],
            subscription_id=checkout_session.id,
            user_id=user.id,
            stripe_status=checkout_session.status,
            stripe_created=checkout_session.created,
            stripe_current_period_start=checkout_session.subscription.current_period_start,
            stripe_current_period_end=checkout_session.subscription.current_period_end,
            stripe_cancel_at_period_end=checkout_session.subscription.cancel_at_period_end,
            stripe_canceled_at=checkout_session.subscription.canceled_at,
        )
        db.add(subscription)
        await db.commit()

        return RedirectResponse(
            url=checkout_session.url, status_code=status.HTTP_303_SEE_OTHER
        )
        # return jsonable_encoder(checkout_session)
    except Exception as e:
        HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/create-portal-session")
async def customer_portal(
    user: Annotated[models.User, Depends(deps.get_current_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    if user.stripe_customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="User must first make a payment before viewing their payment portal",
        )
    with tracer.start_as_current_span("Retrieve subscription"):
        subscription_id = await db.scalar(
            sa.select(models.Subscription.subscription_id).where(
                models.Subscription.user_id == user.id
            )
        )
        if subscription_id is None:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Could not find an existing subscription for user",
            )
    # checkout_session_id = request.form.get("session_id")
    # not sure if this is the same number, lol
    checkout_session = stripe.checkout.Session.retrieve(subscription_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=f"http://{settings.HOST}:{settings.PORT}",
    )
    return RedirectResponse(
        url=portalSession.url, status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/webhook")
async def webhook_received(
    obj: WebHookData,
    stripe_signature: Annotated[str, Header()],
    db: Annotated[AsyncSession, Depends(deps.get_async_session)],
):
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    try:
        event = stripe.Webhook.construct_event(
            # TODO (Jonny): see what this attribute is in Flask and translate it to fastapi
            payload=obj.data,
            sig_header=stripe_signature,
            secret=WEBHOOK_SECRET,
        )
        # data = event["data"] # unused again!
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # Get the type of webhook event sent - used to check the status of PaymentIntents.
    event_type = event["type"]

    try:
        # This is broke, waiting on figuring out the obj.data schema
        subscription = await db.scalar(
            sa.select(models.Subscription).where(
                models.Subscription.subscription_id == obj.data["subscription_id"]
            )
        )
        user = subscription.user
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    match event_type:
        case "checkout.session.completed":
            # TODO (Jonny): something should happen here with the DB
            logger.info("🔔 Payment succeeded!")
            user.is_subscribed = True
            await db.commit()
        case "customer.subscription.trial_will_end":
            # TODO (Jonny): something should happen here with the DB
            logger.info("Subscription trial will end")
        case "customer.subscription.created":
            # TODO (Jonny): something should happen here with the DB?
            logger.info(f"Subscription created {event.id}")
        case "customer.subscription.updated":
            # TODO (Jonny): something should happen here with the DB?
            logger.info(f"Subscription created {event.id}")
        case "customer.subscription.deleted":
            # (stripe comments) handle subscription canceled automatically based
            # upon your subscription settings. Or if the user cancels it.
            # TODO (Jonny): something should happen here with the DB
            logger.info(f"Subscription canceled: {event.id}")
            user.is_subscribed = False
            await db.commit()
        case _:
            logger.error(f"Unhandled event_type: {event_type}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


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


# Usage based


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


# -------------- copied -------------- #

# import React, { useState, useEffect } from 'react';
# import './App.css';

# const ProductDisplay = () => (
#   <section>
#     <div className="product">
#       <Logo />
#       <div className="description">
#         <h3>Starter plan</h3>
#         <h5>$20.00 / month</h5>
#       </div>
#     </div>
#     <form action="/create-checkout-session" method="POST">
#       {/* Add a hidden field with the lookup_key of your Price */}
#       <input type="hidden" name="lookup_key" value="{{PRICE_LOOKUP_KEY}}" />
#       <button id="checkout-and-portal-button" type="submit">
#         Checkout
#       </button>
#     </form>
#   </section>
# );

# const SuccessDisplay = ({ sessionId }) => {
#   return (
#     <section>
#       <div className="product Box-root">
#         <Logo />
#         <div className="description Box-root">
#           <h3>Subscription to starter plan successful!</h3>
#         </div>
#       </div>
#       <form action="/create-portal-session" method="POST">
#         <input
#           type="hidden"
#           id="session-id"
#           name="session_id"
#           value={sessionId}
#         />
#         <button id="checkout-and-portal-button" type="submit">
#           Manage your billing information
#         </button>
#       </form>
#     </section>
#   );
# };

# const Message = ({ message }) => (
#   <section>
#     <p>{message}</p>
#   </section>
# );

# export default function App() {
#   let [message, setMessage] = useState('');
#   let [success, setSuccess] = useState(false);
#   let [sessionId, setSessionId] = useState('');

#   useEffect(() => {
#     // Check to see if this is a redirect back from Checkout
#     const query = new URLSearchParams(window.location.search);

#     if (query.get('success')) {
#       setSuccess(true);
#       setSessionId(query.get('session_id'));
#     }

#     if (query.get('canceled')) {
#       setSuccess(false);
#       setMessage(
#         "Order canceled -- continue to shop around and checkout when you're ready."
#       );
#     }
#   }, [sessionId]);

#   if (!success && message === '') {
#     return <ProductDisplay />;
#   } else if (success && sessionId !== '') {
#     return <SuccessDisplay sessionId={sessionId} />;
#   } else {
#     return <Message message={message} />;
#   }
# }

# const Logo = () => (
#   <svg
#     xmlns="http://www.w3.org/2000/svg"
#     xmlnsXlink="http://www.w3.org/1999/xlink"
#     width="14px"
#     height="16px"
#     viewBox="0 0 14 16"
#     version="1.1"
#   >
#     <defs />
#     <g id="Flow" stroke="none" strokeWidth="1" fill="none" fillRule="evenodd">
#       <g
#         id="0-Default"
#         transform="translate(-121.000000, -40.000000)"
#         fill="#E184DF"
#       >
#         <path
#           d="M127,50 L126,50 C123.238576,50 121,47.7614237 121,45 C121,42.2385763 123.238576,40 126,40 L135,40 L135,56 L133,56 L133,42 L129,42 L129,56 L127,56 L127,50 Z M127,48 L127,42 L126,42 C124.343146,42 123,43.3431458 123,45 C123,46.6568542 124.343146,48 126,48 L127,48 Z"
#           id="Pilcrow"
#         />
#       </g>
#     </g>
#   </svg>
# );
