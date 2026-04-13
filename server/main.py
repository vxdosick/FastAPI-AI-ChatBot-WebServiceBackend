from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.database import engine, Base
from routes.auth_endpoints import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="FastAPI-AI-ChatBot-WebServiceBackend", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"status": "Server is running"}