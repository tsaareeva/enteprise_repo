import json
from app.schemas import WelcomeEmailMessage
from app.rabbitmq import rabbitmq
from app.config import settings
from datetime import datetime

async def send_welcome_email(customer_id: int, email: str, first_name: str):
    message_data = WelcomeEmailMessage(
        customer_id=customer_id,
        email=email,
        first_name=first_name,
        created_at=datetime.now()
    )

    message_body = json.dumps(message_data.model_dump(), default=str).encode()

    if settings.MODE == "mock":
        await rabbitmq.mock_publish(
            settings.EMAIL_QUEUE,
            message_body,
            {"message_type": "welcome-email", "customer_id": str(customer_id)}
        )
    else:
        channel = rabbitmq.get_channel()
        if not channel:
            print("RabbitMQ не подключен")
            return

        import aio_pika
        message = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        message.headers["message_type"] = "welcome-email"

        await channel.default_exchange.publish(
            message,
            routing_key=settings.EMAIL_QUEUE
        )
        print(f"Сообщение отправлено в {settings.EMAIL_QUEUE}")