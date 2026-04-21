from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, BackgroundTasks, Depends
from repositories.auth_repositories import UserRepository
from schemas.auth_schemas import UserCreate
from config.config import SECRET_KEY, ALGORITHM, MAIL_CONFIG
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi.security import OAuth2PasswordBearer
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.auth_repositories import UserRepository

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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

class AuthService:
    def __init__(self, repo: UserRepository, mail_service: MailService):
        self.repo = repo
        self.mail_service = mail_service

    def hash_password(self, password: str):
        return PWD_CONTEXT.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    def create_token(self, data: dict, expires_delta: timedelta, token_type: str = "access"):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def register_new_user(self, user_in: UserCreate, background_tasks: BackgroundTasks):
        if await self.repo.get_user_by_email(user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if await self.repo.get_user_by_username(user_in.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        
        hashed_pwd = self.hash_password(user_in.password)
        user_data = {
            "username": user_in.username,
            "email": user_in.email,
            "hashed_password": hashed_pwd
        }
        user = await self.repo.create_user(user_data)
        
        # Send verification email
        verify_token = self.create_token({"sub": user.email}, timedelta(hours=24), "verify")
        
        background_tasks.add_task(self.mail_service.send_verification_email, user.email, verify_token)
        
        return user

    async def authenticate_user(self, username, password):
        user = await self.repo.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def verify_email_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            t_type: str = payload.get("type")
            if email is None or t_type != "verify":
                raise ValueError()
        except (JWTError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")

        user = await self.repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await self.repo.activate_user(user)
        return {"message": "Account activated"}
    
    async def logout(self, token: str):
        if not await self.repo.is_token_blacklisted(token):
            await self.repo.add_token_to_blacklist(token)

    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: AsyncSession = Depends(get_db)
    ):
        repo = UserRepository(db) 
        
        if await repo.is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token blacklisted")
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
            
        user = await repo.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
    
    async def request_password_reset(self, email: str, background_tasks: BackgroundTasks):
        user = await self.repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        reset_token = self.create_token({"sub": user.email}, timedelta(hours=1), "reset")

        background_tasks.add_task(self.mail_service.send_reset_password_email, user.email, reset_token)

    async def reset_password_confirm(self, token: str, new_password: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            t_type: str = payload.get("type")
            if email is None or t_type != "reset":
                raise ValueError()
        except (JWTError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        user = await self.repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        hashed_pwd = self.hash_password(new_password)
        await self.repo.update_user_password(user, hashed_pwd)
        return {"message": "Password reset successful"}