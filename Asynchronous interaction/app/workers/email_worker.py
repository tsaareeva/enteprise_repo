import asyncio
from app.consumer import start_consumer

if __name__ == "__main__":
    print("Запуск воркера обработки email")
    asyncio.run(start_consumer())