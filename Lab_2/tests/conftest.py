import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User, Role

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_token(client):
    client.post("/api/auth/register", json={"username": "u", "password": "p123"})
    r = client.post("/api/auth/login", data={"username": "u", "password": "p123"})
    return r.json()["access_token"]

@pytest.fixture
def admin_token(client):
    client.post("/api/auth/register", json={"username": "admin", "password": "a123"})
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "admin").first()
    role = db.query(Role).filter(Role.name == "ROLE_ADMIN").first()
    if not role:
        role = Role(name="ROLE_ADMIN")
        db.add(role)
        db.commit()
        db.refresh(role)
    user.roles.append(role)
    db.commit()
    db.close()
    r = client.post("/api/auth/login", data={"username": "admin", "password": "a123"})
    return r.json()["access_token"]

@pytest.fixture
def customer(client, admin_token):
    r = client.post("/api/v1/customers", json={
        "first_name": "John", "last_name": "Doe", "email": "j@example.com"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    return r.json()