import subprocess
import time
import uuid
from datetime import datetime, timedelta

import requests
import stripe
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker
from tenacity import retry, stop_after_attempt, wait_exponential

from app import models

stripe.api_key = (
    "sk_test_51NiAqMCJiKhdlW4v8mN2P5MYa5J2k1eN13ZFz1dkQtzBU0q"
    "VeizSzJu4q9sKDrehkkmCWDBj8XGxGDoRThw1Y9u800nVEK7yGv"
)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
PRICE_LOOKUP_KEY = "basic_monthly"
base = "http://localhost:8000"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=Session, expire_on_commit=False)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def launch_webhook_listener():
    cmd = (
        "stripe listen --forward-to localhost:8000/stripe/webhook --events checkout.session.completed"
        ",customer.subscription.updated,customer.subscription.deleted"
    )
    subprocess.run(cmd, shell=True)
    # .decode("utf-8")
    # token = re.search(r"secret is (\w+)\s+", output).group(1)
    # print("Webhook token:", token)
    # return token


@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def test_one(user_id: uuid.UUID):
    with SessionLocal() as db:
        r = (
            db.query(models.Subscription)
            .where(models.Subscription.user_id == user_id)
            .order_by(models.Subscription.created_at.desc())
            .all()
        )
        sub = r[0]
    if (
        sub
        and sub.stripe_status == "active"
        and sub.stripe_current_period_end > time.time() + (60 * 60 * 24 * 20)
    ):
        print(
            f"{bcolors.BOLD}Subscription entered into the database: {bcolors.OKGREEN}SUCCESS{bcolors.ENDC}"
        )
        return sub
    else:
        raise ValueError(
            f"{bcolors.BOLD}Subscription entered into the database: {bcolors.FAIL}FAILURE{bcolors.ENDC}"
        )


@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def test_two(user_id: uuid.UUID):
    with SessionLocal() as db:
        r = (
            db.query(models.Subscription)
            .where(models.Subscription.user_id == user_id)
            .order_by(models.Subscription.created_at.desc())
            .all()
        )
        sub = r[0]
    if (
        sub
        and sub.stripe_status == "active"
        and sub.stripe_current_period_end > time.time() + (60 * 60 * 24 * 32)
    ):
        print(
            f"{bcolors.BOLD}Subscription advance 1 month: {bcolors.OKGREEN}SUCCESS{bcolors.ENDC}"
        )
        return sub
    else:
        raise ValueError(
            f"{bcolors.BOLD}Subscription advance 1 month: {bcolors.FAIL}FAILURE{bcolors.ENDC}"
        )


@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def test_three(user_id: uuid.UUID):
    with SessionLocal() as db:
        r = (
            db.query(models.Subscription)
            .where(models.Subscription.user_id == user_id)
            .order_by(models.Subscription.created_at.desc())
            .all()
        )
        sub = r[0]
    print("status:", sub.stripe_status, "cancel:", sub.stripe_cancel_at_period_end)
    if sub and sub.stripe_status == "active" and sub.stripe_cancel_at_period_end:
        print(
            f"{bcolors.BOLD}Subscription scheduled for termination: {bcolors.OKGREEN}SUCCESS{bcolors.ENDC}"
        )
        return sub
    else:
        raise ValueError(
            f"{bcolors.BOLD}Subscription scheduled for termination: {bcolors.FAIL}FAILURE{bcolors.ENDC}"
        )


@retry(stop=stop_after_attempt(5), wait=wait_exponential())
def test_four(user_id: uuid.UUID):
    with SessionLocal() as db:
        r = (
            db.query(models.Subscription)
            .where(models.Subscription.user_id == user_id)
            .order_by(models.Subscription.created_at.desc())
            .all()
        )
        sub = r[0]
    print("status:", sub.stripe_status, "cancel:", sub.stripe_cancel_at_period_end)
    if sub and sub.stripe_status != "active":
        print(
            f"{bcolors.BOLD}Subscription status changed to cancelled: {bcolors.OKGREEN}SUCCESS{bcolors.ENDC}"
        )
        return sub
    else:
        raise ValueError(
            f"{bcolors.BOLD}Subscription status changed to cancelled: {bcolors.FAIL}FAILURE{bcolors.ENDC}"
        )


def main():
    # print("Starting webhook listener")
    # webhook_token = launch_webhook_listener()

    print("Getting the client reference id")
    with requests.Session() as client:
        r = client.post(
            base + "/auth/register",
            json=dict(email="test@example.com", password="password"),
        )
        r = client.post(
            base + "/auth/cookies/login",
            data=dict(username="test@example.com", password="password"),
        )
        assert r.status_code == 204, r.json()
        assert r.cookies
        headers = {
            "Cookie": "; ".join(
                [f"{name}={value}" for name, value in client.cookies.items()][-1:]
            )
        }
        user_id = uuid.UUID(
            client.get(base + "/users/me", headers=headers).json()["id"]
        )
        r = client.get(base + "/stripe/checkout-token", headers=headers)
        client_reference_id = r.json()["token"]

    print("Setting up clock")
    clock = stripe.test_helpers.TestClock.create(
        frozen_time=int(time.time()),
        name="Monthly renewal",
    )
    print("Retrieving preconfigured price:", PRICE_LOOKUP_KEY)
    price = stripe.Price.list(lookup_keys=[PRICE_LOOKUP_KEY]).data[0]

    print("Creating customer")
    customer = stripe.Customer.create(
        email="seymour.butts@example.com",
        test_clock=clock.stripe_id,
        payment_method="pm_card_visa",
        invoice_settings={"default_payment_method": "pm_card_visa"},
    )

    print("Creating checkout session")
    checkout_session = stripe.checkout.Session.create(
        success_url="https://localhost:3000/account",
        line_items=[{"price": price.stripe_id, "quantity": 1}],
        mode="subscription",
        client_reference_id=client_reference_id,
        customer=customer.id,
    )

    input(
        f"Please checkout with card 4242-4242-4242-42424 at the following url: {checkout_session.url}"
    )

    sub = test_one(user_id=user_id)

    print("Advancing clock by 31 days")
    stripe.test_helpers.TestClock.advance(
        clock.stripe_id,
        frozen_time=int((datetime.utcnow() + timedelta(days=31)).timestamp()),
    )

    sub = test_two(user_id=user_id)

    print("Cancelling the subscription by end of the term")
    stripe.Subscription.modify(sub.stripe_subscription_id, cancel_at_period_end=True)

    sub = test_three(user_id=user_id)

    print("Advancing clock by 62 days")
    stripe.test_helpers.TestClock.advance(
        clock.stripe_id,
        frozen_time=int((datetime.utcnow() + timedelta(days=62)).timestamp()),
    )
    time.sleep(3)

    test_four(user_id=user_id)


if __name__ == "__main__":
    main()
