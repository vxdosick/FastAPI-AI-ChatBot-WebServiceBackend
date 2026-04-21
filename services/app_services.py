import secrets
from fastapi import HTTPException
from repositories.app_repositories import AppRepository
from schemas.app_schemas import BotCreate

class AppService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    async def create_new_bot(self, user_id: int, bot_data: BotCreate):
        api_key = f"at_{secrets.token_urlsafe(32)}"
        
        return await self.repo.create_user_bot(
            user_id=user_id, 
            bot_data=bot_data, 
            api_key=api_key
        )

    async def validate_bot_access(self, api_key: str, origin: str):
        bot = await self.repo.get_bot_by_api_key(api_key)

        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        if bot.allowed_domain and bot.allowed_domain != "*":
            if not origin or bot.allowed_domain not in origin:
                if "localhost" not in (origin or "") and "127.0.0.1" not in (origin or ""):
                    raise HTTPException(status_code=403, detail="Domain not allowed")

        settings = bot.settings if bot.settings else {}

        return {
            "status": "success",
            "bot_id": bot.id,
            "bot_name": bot.name,
            "settings": {
                "theme_color": settings.get("theme_color", "#4f46e5"),
                "system_prompt": settings.get("system_prompt", "Default help prompt...")
            }
        }
    
    async def get_all_user_bots(self, user_id: int):
        return await self.repo.get_user_bots(user_id)