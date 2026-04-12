from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from repositories.repositories import UserRepository
from services.services import AuthService, timedelta
from schemas.schemas import UserCreate, UserOut, Token, VerificationRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_auth_service(db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    return AuthService(repo)

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    return await service.register_new_user(user_in)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)):
    user = await service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Email not verified")

    access_token = service.create_token({"sub": user.username}, timedelta(minutes=30))
    refresh_token = service.create_token({"sub": user.username}, timedelta(days=7))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/verify-email")
async def verify_email(req: VerificationRequest, db: AsyncSession = Depends(get_db)):
    username = req.token.split("_")[0]
    repo = UserRepository(db)
    user = await repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repo.activate_user(user)
    return {"message": "Account activated"}

@router.post("/logout")
async def logout(req: LogoutRequest, service: AuthService = Depends(get_auth_service)):
    await service.logout(req.refresh_token)
    return {"message": "Successfully logged out. Token invalidated."}