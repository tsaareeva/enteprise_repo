import aio_pika
import asyncio
from typing import Optional, Callable, Any
from app.config import settings

class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._mock_queue: list = []
        self._mock_handlers: dict = {}

    async def connect(self):
        if settings.MODE == "mock":
            return

        try:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASS
            )
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(settings.EMAIL_QUEUE, durable=True)
            await self.channel.declare_queue(settings.REPORT_QUEUE, durable=True)
            print(f"Подключено к RabbitMQ")
        except Exception as e:
            print(f"Не удалось подключиться к RabbitMQ: {e}")
            print("Переключитесь в режим имитации: MODE=mock в .env")
            raise

    async def disconnect(self):
        if self.connection and settings.MODE == "rabbitmq":
            await self.connection.close()

    def get_channel(self):
        return self.channel

    async def mock_publish(self, queue_name: str, body: bytes, headers: dict = None):
        self._mock_queue.append({
            "queue": queue_name,
            "body": body,
            "headers": headers or {}
        })
        print(f"[MOCK] Сообщение в {queue_name}: {body[:100]}...")

        if queue_name in self._mock_handlers:
            asyncio.create_task(self._mock_handlers[queue_name](body))

    async def mock_consume(self, queue_name: str, callback: Callable):
        self._mock_handlers[queue_name] = callback
        print(f"[MOCK] Подписка на {queue_name}")

    async def process_mock_queue(self):
        while self._mock_queue:
            item = self._mock_queue.pop(0)
            if item["queue"] in self._mock_handlers:
                class MockMessage:
                    def __init__(self, body):
                        self.body = body

                    async def process(self):
                        return self

                    def __aenter__(self):
                        return self

                    def __aexit__(self, *args):
                        pass

                await self._mock_handlers[item["queue"]](MockMessage(item["body"]))

rabbitmq = RabbitMQConnection()