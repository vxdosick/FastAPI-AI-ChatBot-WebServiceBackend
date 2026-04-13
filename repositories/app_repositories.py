import secrets
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.app_models import Bot
from schemas.app_schemas import BotCreate

class AppRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_bot(self, user_id: int, bot_data: BotCreate) -> Bot:

        generated_key = f"at_{secrets.token_urlsafe(32)}"
        
        db_bot = Bot(
            name=bot_data.name,
            allowed_domain=bot_data.allowed_domain,
            api_key=generated_key,
            owner_id=user_id
        )
        self.session.add(db_bot)
        await self.session.commit()
        await self.session.refresh(db_bot)
        return db_bot

    async def get_bot_by_api_key(self, api_key: str) -> Bot | None:
        result = await self.session.execute(
            select(Bot).where(Bot.api_key == api_key)
        )
        return result.scalar_one_or_none()
    
    async def get_user_bots(self, user_id: int) -> list[Bot]:
        result = await self.session.execute(
            select(Bot).where(Bot.owner_id == user_id)
        )
        return result.scalars().all()