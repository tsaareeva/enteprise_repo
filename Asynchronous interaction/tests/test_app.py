import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, Base
from sqlalchemy import text
import time
import asyncio

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_database():
    yield

    async def clear_db():
        async with engine.begin() as conn:
            await conn.execute(text("DELETE FROM customers"))

    asyncio.run(clear_db())

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "status" in data
    print("\ntest_root_endpoint PASSED")

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("test_health_check PASSED")

def test_create_customer():
    customer_data = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": f"test_{time.time()}@example.com"
    }

    response = client.post("/api/v1/customers", json=customer_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = response.json()
    assert data["first_name"] == "Иван"
    assert data["last_name"] == "Иванов"
    assert "id" in data
    assert data["id"] is not None

    print(f"test_create_customer PASSED (ID: {data['id']})")

def test_create_customer_validation():
    invalid_data = {
        "first_name": "",
        "last_name": "Иванов",
        "email": f"validation_{time.time()}@example.com"
    }

    response = client.post("/api/v1/customers", json=invalid_data)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("test_create_customer_validation PASSED")

def test_create_customer_invalid_email():
    invalid_data = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "not-an-email"
    }

    response = client.post("/api/v1/customers", json=invalid_data)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    print("test_create_customer_invalid_email PASSED")


def test_get_customer_by_id():
    customer_data = {
        "first_name": "Пётр",
        "last_name": "Петров",
        "email": f"petr_{time.time()}@example.com"
    }

    create_response = client.post("/api/v1/customers", json=customer_data)
    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/customers/{customer_id}")
    assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}: {get_response.text}"

    data = get_response.json()
    assert data["id"] == customer_id
    assert data["first_name"] == "Пётр"

    print(f"test_get_customer_by_id PASSED (ID: {customer_id})")

def test_get_nonexistent_customer():
    response = client.get("/api/v1/customers/99999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print("test_get_nonexistent_customer PASSED")

def test_get_all_customers():
    customers_data = [
        {"first_name": "Анна", "last_name": "Смирнова", "email": f"anna_{time.time()}@example.com"},
        {"first_name": "Борис", "last_name": "Козлов", "email": f"boris_{time.time()}@example.com"},
    ]

    for customer in customers_data:
        response = client.post("/api/v1/customers", json=customer)
        assert response.status_code == 201

    response = client.get("/api/v1/customers?skip=0&limit=10")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert isinstance(data, list)

    print(f"test_get_all_customers PASSED (found: {len(data)})")


def test_delete_customer():
    customer_data = {
        "first_name": "Мария",
        "last_name": "Соколова",
        "email": f"maria_{time.time()}@example.com"
    }

    create_response = client.post("/api/v1/customers", json=customer_data)
    customer_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/customers/{customer_id}")
    assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}"

    get_response = client.get(f"/api/v1/customers/{customer_id}")
    assert get_response.status_code == 404, f"Expected 404 after delete, got {get_response.status_code}"

    print(f"test_delete_customer PASSED (ID: {customer_id})")


def test_duplicate_email():
    unique_email = f"duplicate_{time.time()}@example.com"

    customer_data = {
        "first_name": "Ольга",
        "last_name": "Новикова",
        "email": unique_email
    }

    response1 = client.post("/api/v1/customers", json=customer_data)
    assert response1.status_code == 201, f"First creation failed: {response1.text}"

    response2 = client.post("/api/v1/customers", json=customer_data)
    assert response2.status_code == 400, f"Expected 400 for duplicate, got {response2.status_code}: {response2.text}"

    print("test_duplicate_email PASSED")


def test_api_response_time():
    customer_data = {
        "first_name": "Тест",
        "last_name": "Тестов",
        "email": f"timing_{time.time()}@example.com"
    }

    start = time.time()
    response = client.post("/api/v1/customers", json=customer_data)
    elapsed = time.time() - start

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    assert elapsed < 1.5, f"API ответил медленно: {elapsed:.2f} сек"

    print(f"test_api_response_time PASSED ({elapsed * 1000:.0f} мс)")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])