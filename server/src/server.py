from io import BytesIO
from dotenv import load_dotenv
from time import sleep

import pika
import os

load_dotenv()

# RabbitMQ Setup

def video_callback(ch, method, properties, body):
    global channel

    print(f"Received Video Frame: {body}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # channel.basic_publish(exchange='', routing_key='speed', body='80')


def report_callback(ch, method, properties, body):
    print("Received Report")
    print(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    # Send email to the user


def on_channel_open(chn):
    global channel
    
    channel = chn
    
    chn.basic_qos(prefetch_count=1)

    chn.queue_declare(queue='video')
    chn.queue_declare(queue='speed')
    chn.queue_declare(queue='report')

    chn.basic_consume(queue='video', on_message_callback=video_callback)
    chn.basic_consume(queue='report', on_message_callback=report_callback)


def on_open(connection):
    connection.channel(on_open_callback=on_channel_open)


url = os.getenv("CLOUDAMQP_URL")
params = pika.URLParameters(url)
connection = pika.SelectConnection(params, on_open_callback=on_open)
channel = None

if __name__ == '__main__':
    try:
        print("Running PiSpeedCam Server Thread!")
        connection.ioloop.start()
    except KeyboardInterrupt:
        print('Finished Running')
        connection.close()
    