from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from repositories.repositories import UserRepository
from schemas.schemas import UserCreate

SECRET_KEY = "SUPER_SECRET_KEY_DO_NOT_SHARE"
ALGORITHM = "HS256"
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def hash_password(self, password: str):
        return PWD_CONTEXT.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    def create_token(self, data: dict, expires_delta: timedelta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def register_new_user(self, user_in: UserCreate):
        hashed_pwd = self.hash_password(user_in.password)
        user_data = {
            "username": user_in.username,
            "email": user_in.email,
            "hashed_password": hashed_pwd
        }
        user = await self.repo.create_user(user_data)
        print(f"--- EMAIL SENT TO {user.email}: Verification Token: {user.username}_verify_token ---")
        return user

    async def authenticate_user(self, username, password):
        user = await self.repo.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    async def logout(self, token: str):
        await self.repo.add_token_to_blacklist(token)

    async def is_token_valid(self, token: str):
        if await self.repo.is_token_blacklisted(token):
            return False
        return True