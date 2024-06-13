from io import BytesIO
from dotenv import load_dotenv
from time import sleep

import pika
import os

load_dotenv()

# RabbitMQ Setup

url = os.getenv("CLOUDAMQP_URL")
# params = pika.URLParameters(url)
params = pika.ConnectionParameters('localhost')
connection = pika.SelectConnection(params)
channel = None
    