import pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

def publish_event(event_type: str, data: dict):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    exchange_name = 'orders_exchange'
    queue_name = 'orders_events'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(queue=queue_name, exchange=exchange_name)
    channel.basic_publish(exchange=exchange_name, routing_key='', body=json.dumps({'type': event_type, 'data': data}))
    connection.close()