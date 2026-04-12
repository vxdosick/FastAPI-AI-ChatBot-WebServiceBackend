from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import User, BlacklistedToken

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str):
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str):
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict):
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.refresh(user)
        return user

    async def activate_user(self, user: User):
        user.is_active = True
        await self.session.commit()

    async def refresh(self, obj):
        await self.session.refresh(obj)

    async def add_token_to_blacklist(self, token: str):
        blacklisted = BlacklistedToken(token=token)
        self.session.add(blacklisted)
        await self.session.commit()

    async def is_token_blacklisted(self, token: str) -> bool:
        result = await self.session.execute(
            select(BlacklistedToken).where(BlacklistedToken.token == token)
        )
        return result.scalar_one_or_none() is not None