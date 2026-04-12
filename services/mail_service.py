from fastapi_mail import FastMail, MessageSchema, MessageType
from config.config import MAIL_CONFIG

class MailService:
    def __init__(self):
        self.fastmail = FastMail(MAIL_CONFIG)

    async def send_verification_email(self, email: str, token: str):
        # Frontend public URL
        verification_url = f"http://localhost:8000/auth/verify-email?token={token}"
        
        html = f"""
        <html>
            <body>
                <p>Thank you for registering!</p>
                <p>Please click the link below to verify your email address:</p>
                <a href="{verification_url}">{verification_url}</a>
                <p>Url will expire in 24 hours</p>
            </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Email Verification",
            recipients=[email],
            body=html,
            subtype=MessageType.html
        )
        
        await self.fastmail.send_message(message)


    async def send_reset_password_email(self, email: str, token: str):
        # Frontend public URL
        reset_url = f"http://localhost:8000/auth/reset-password-confirm?token={token}"
        
        html = f"""
        <html>
            <body>
                <p>Looks like you have requested to reset your password</p>
                <p>Please click the link below to reset your password:</p>
                <a href="{reset_url}">{reset_url}</a>
                <p>If you did not request a password reset, please ignore this email</p>
            </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Password Reset",
            recipients=[email],
            body=html,
            subtype=MessageType.html
        )

        await self.fastmail.send_message(message)