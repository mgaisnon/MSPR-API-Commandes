import pika
import json
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

def publish_event(event_type: str, data: dict):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='orders_events', durable=True)
    channel.basic_publish(exchange='', routing_key='orders_events', body=json.dumps({'type': event_type, 'data': data}))
    connection.close()