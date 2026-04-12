from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from repositories.repositories import UserRepository
from schemas.schemas import UserCreate
from config.config import SECRET_KEY, ALGORITHM

from services.mail_service import MailService

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

    async def register_new_user(self, user_in: UserCreate):
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
        
        await self.mail_service.send_verification_email(user.email, verify_token)
        
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

    async def get_current_user(self, token: str):
        if await self.repo.is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token blacklisted")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
            
        user = await self.repo.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    async def request_password_reset(self, email: str):
        user = await self.repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        reset_token = self.create_token({"sub": user.email}, timedelta(hours=1), "reset")
        await self.mail_service.send_reset_password_email(user.email, reset_token)

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