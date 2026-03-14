from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.database import engine, Base
from app.routers import auth, customers
from app.models import Role
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lab_2: Security, caching, and advanced API")

app.include_router(auth.router)
app.include_router(customers.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "message": str(exc)})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": "Validation Error", "errors": exc.errors()})

from sqlalchemy.orm import Session
from app.database import SessionLocal
def seed_roles():
    db = SessionLocal()
    if not db.query(Role).filter(Role.name == "ROLE_ADMIN").first():
        db.add(Role(name="ROLE_ADMIN"))
        db.commit()
    db.close()

seed_roles()

def print_startup_message():
    print("Открой: http://localhost:8000/docs")

if __name__ == "__main__":
    print_startup_message()
    uvicorn.run(app, host="0.0.0.0", port=8000)