import json
import time

import pika
import requests
from decouple import config


def callback(ch, method, properties, body):
    order_id = json.loads(body)["order_id"]
    print(
        f"Received Order ID: {order_id}",
    )

    response = requests.post(
        config("DJANGO_SERVER_URL").rstrip("/") + "/process_order/",
        json={"order_id": order_id},
    )
    if response.status_code == 200:
        print(f"Order {order_id} processed successfully.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    elif response.status_code == 404:
        print(f"Order {order_id} not found")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print(f"Failed to process order {order_id}.")


def main():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.URLParameters(
                    f"amqp://{config('RABBITMQ_DEFAULT_USER')}:{config('RABBITMQ_DEFAULT_PASS')}@rabbitmq:5672"
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue="order_queue", durable=True)
            channel.basic_consume(queue="order_queue", on_message_callback=callback)
            print("Waiting for messages.")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed, retrying in 5 seconds...")
            time.sleep(5)
        except pika.exceptions.ConnectionClosedByBroker:
            print("Connection closed by broker, connecting in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
