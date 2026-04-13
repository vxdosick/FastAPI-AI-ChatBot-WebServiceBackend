from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services.app_services import AppService
from repositories.app_repositories import AppRepository
from services.auth_services import AuthServices, get_current_user
from schemas.app_schemas import BotCreate, BotOut

router = APIRouter(prefix="/app", tags=["Application"])

def get_app_service(db: AsyncSession = Depends(get_db)):
    return AppService(AppRepository(db))

@router.post("/bots", response_model=BotOut)
async def create_bot(
    bot_data: BotCreate,
    current_user = Depends(get_current_user),
    service: AppService = Depends(get_app_service)
):
    return await service.create_new_bot(current_user.id, bot_data)

@router.get("/public/validate/{api_key}")
async def validate_widget(
    api_key: str,
    request: Request,
    service: AppService = Depends(get_app_service)
):
    origin = request.headers.get("origin") or request.headers.get("referer") or ""
    return await service.validate_bot_access(api_key, origin)