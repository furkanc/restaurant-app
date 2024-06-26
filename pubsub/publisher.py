import json
import time

import pika
from decouple import config
from django.conf import settings


class PikaPublisher:
    def __init__(self, host=settings.RABBITMQ_HOST, queue=settings.RABBITMQ_QUEUE):
        self.host = host
        self.queue = queue
        self.connection = None
        self.channel = None
        self._user = config("RABBITMQ_DEFAULT_USER")
        self._password = config("RABBITMQ_DEFAULT_PASS")
        self.connect()

    def connect(self):
        while True:
            try:
                self.connection = pika.BlockingConnection(
                    pika.URLParameters(f"amqp://{self._user}:{self._password}@rabbitmq:5672")
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                break
            except pika.exceptions.AMQPConnectionError:
                print("Connection failed, retrying in 5 seconds...")
                time.sleep(5)

    def publish(self, message):
        if not self.channel or self.channel.is_closed:
            self.connect()
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
