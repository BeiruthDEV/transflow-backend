import os
from faststream.rabbit import RabbitBroker

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

broker = RabbitBroker(RABBITMQ_URL)

async def get_broker():

    return broker

async def publicar_corrida(dados_corrida: dict):

    await broker.publish(
        message=dados_corrida,
        queue="corridas_queue"
    )
    print(f"📤 [Evento Enviado] Corrida {dados_corrida.get('id_corrida')} enviada para processamento.")