from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.database import engine, Base
from routes.auth_endpoints import router as auth_router
from routes.app_endpoints import router as app_router
from middlewares.app_middlewares import add_cors_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="FastAPI-AI-ChatBot-WebServiceBackend", version="1.0.0", lifespan=lifespan)

add_cors_middleware(app)

app.include_router(auth_router)
app.include_router(app_router)

@app.get("/")
async def root():
    return {"status": "Server is running"}