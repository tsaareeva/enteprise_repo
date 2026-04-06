from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.rabbitmq import rabbitmq
from app.api.routes import router
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await rabbitmq.connect()
    print("Открой в браузере: http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    yield
    print("\nОстановка приложения")
    await rabbitmq.disconnect()

app = FastAPI(
    title="Lab 3: Async Messaging",
    description="Асинхронное взаимодействие с очередями сообщений",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "message": "Lab 3: Async Messaging API",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "mode": "mock"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")