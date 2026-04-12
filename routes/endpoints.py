from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from repositories.repositories import UserRepository
from services.services import AuthService
from schemas.schemas import UserCreate, UserOut, Token, VerificationRequest, LogoutRequest, ForgotPasswordRequest, ResetPasswordConfirm
from config.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from datetime import timedelta

from services.mail_service import MailService

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_auth_service(db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    mail_service = MailService()
    return AuthService(repo, mail_service)

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    return await service.register_new_user(user_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)):
    user = await service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    access_token = service.create_token(
        {"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = service.create_token(
        {"sub": user.username}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/verify-email")
async def verify_email(req: VerificationRequest, service: AuthService = Depends(get_auth_service)):
    return await service.verify_email_token(req.token)

@router.post("/logout")
async def logout(req: LogoutRequest, service: AuthService = Depends(get_auth_service)):
    await service.logout(req.refresh_token)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserOut)
async def get_me(token: str = Depends(oauth2_scheme), service: AuthService = Depends(get_auth_service)):
    return await service.get_current_user(token)

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)):
    await service.request_password_reset(req.email)
    return {"message": "Password reset email sent"}

@router.post("/reset-password-confirm")
async def reset_password_confirm(req: ResetPasswordConfirm, service: AuthService = Depends(get_auth_service)):
    return await service.reset_password_confirm(req.token, req.new_password)