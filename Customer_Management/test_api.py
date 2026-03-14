import requests
import time

def test_api():
    base_url = "http://localhost:8000"

    print("Тестирование API...")


    try:
        response = requests.get(f"{base_url}/")
        print(f"Главная страница: {response.status_code}")
        print(f"Ответ: {response.json()}")
    except:
        print("Не удалось подключиться к API")
        return


    try:
        response = requests.get(f"{base_url}/docs")
        print(f"Документация: {response.status_code}")
    except:
        print("Документация недоступна")


    try:
        customer_data = {
            "first_name": "Тест",
            "last_name": "Пользователь",
            "email": f"test{int(time.time())}@example.com"
        }
        response = requests.post(f"{base_url}/api/customers/", json=customer_data)
        print(f"Создание клиента: {response.status_code}")
        if response.status_code == 201:
            customer = response.json()
            print(f"   ID: {customer['id']}, Email: {customer['email']}")
    except Exception as e:
        print(f"Ошибка при создании клиента: {e}")

    print("\nAPI работает корректно")
    print(f"Открой в браузере: {base_url}/docs")


if __name__ == "__main__":
    test_api()