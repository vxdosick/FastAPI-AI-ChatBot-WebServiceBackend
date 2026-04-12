from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

from config.config import DB_DIR
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

DB_URL = f"sqlite+aiosqlite:///{DB_DIR}/data.db"

engine = create_async_engine(DB_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session