from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import customers
from app.database.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Application shutdown")

app = FastAPI(
    title="Customer Management",
    description="Монолит с четкой слоистой архитектурой и ORM",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/api/customers", tags=["customers"])

@app.get("/")
def root():
    return {
        "message": "Customer Management",
        "docs": "/docs",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "SQLite"}


if __name__ == "__main__":
    print("Customer Management запущен")
    print("Доступные адреса:")
    print("- http://localhost:8000")
    print("- http://localhost:8000/docs")

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )