from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer

app = FastAPI()

# Replace these with your own email server and secret key settings
EMAIL_SERVER = "your_email_server"
EMAIL_PORT = 587
EMAIL_USER = "your_email_username"
EMAIL_PASSWORD = "your_email_password"
SECRET_KEY = "your_secret_key_for_token_generation"
VERIFICATION_EMAIL_EXPIRATION = 3600  # Token expiration time in seconds (1 hour)

serializer = URLSafeTimedSerializer(SECRET_KEY)


def send_verification_email(email: str, token: str):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    subject = "Email Verification - YourAppName"
    body = f"Click the link to verify your email: http://yourdomain.com/verify_email?token={token}"
    sender_email = "your_email_sender"
    receiver_email = email

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to send verification email."
        )


@app.post("/register/")
async def register_user(
    email: str = Query(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
):
    token = serializer.dumps(email)
    send_verification_email(email, token)
    return JSONResponse(content={"message": "Verification email sent successfully."})


@app.get("/verify_email/")
async def verify_email(token: str = Query(...)):
    try:
        email = serializer.loads(token, max_age=VERIFICATION_EMAIL_EXPIRATION)
    except Exception:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token."
        )

    # Your email verification logic goes here
    # For example, mark the email as verified in the database or update the user record.

    return JSONResponse(content={"message": "Email verified successfully."})
