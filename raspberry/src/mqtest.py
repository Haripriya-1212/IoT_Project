from dotenv import load_dotenv
import pika
import os

load_dotenv()

url = os.getenv("CLOUDAMQP_URL")
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='Hello World!')

print(" [x] Sent 'Hello World!'")

connection.close()