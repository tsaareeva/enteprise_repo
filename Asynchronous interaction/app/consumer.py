import asyncio
import json
import aio_pika
from app.rabbitmq import rabbitmq
from app.config import settings

async def process_email_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())

            print("Получено сообщение для отправки email")
            print(f"Customer ID: {data.get('customer_id')}")
            print(f"Email: {data.get('email')}")
            print(f"First Name: {data.get('first_name')}")
            print(f"Created At: {data.get('created_at')}")

            print("Начало обработки сообщения")
            await asyncio.sleep(2)

            print(f"[ИМИТАЦИЯ] Приветственное письмо отправлено на: {data.get('email')}")
            print(f"Email успешно обработан для клиента ID: {data.get('customer_id')}")

        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")
            raise


async def start_consumer():
    await rabbitmq.connect()

    channel = rabbitmq.get_channel()
    queue = await channel.get_queue(settings.EMAIL_QUEUE)

    print(f"Ожидание сообщений в очереди {settings.EMAIL_QUEUE}")
    print("Press Ctrl+C to exit\n")

    await queue.consume(process_email_message)

    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(start_consumer())
    except KeyboardInterrupt:
        print("\nОстановка потребителя")
        asyncio.run(rabbitmq.disconnect())