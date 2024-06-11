from io import BytesIO
from time import sleep
from threading import Thread

from picamera import PiCamera
from gpiozero import Buzzer
from dotenv import load_dotenv

import pika
import os

load_dotenv()

buzzer = Buzzer(17)

# RabbitMQ Setup

url = os.getenv("CLOUDAMQP_URL")
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='video')
channel.queue_declare(queue='speed')
channel.queue_declare(queue='report')

def poll_camera_capture():
    capture_stream = BytesIO()
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    
    while(True):
        camera.capture(capture_stream, 'jpeg')
        capture_stream.seek(0)
        channel.basic_publish(exchange='', routing_key='video', body=capture_stream.read())
        sleep(1)


def ring_buzzer():
    global buzzer
    buzzer_time = 2
    
    buzzer.on()
    sleep(buzzer_time)
    buzzer.off()


current_speed = 20

def callback(ch, method, properties, body):
    global current_speed
    
    speed_limit = int(body)

    if current_speed > speed_limit:
        ring_buzzer()
        channel.basic_publish(exchange='', routing_key='report', body='Speeding Found!')


if __name__ == '__main__':
    capture_thread = Thread(target=poll_camera_capture)
    
    capture_thread.start()
    channel.basic_consume('speed', callback, auto_ack=True)

    print("Running PiSpeedCam!")
    
    channel.stop_consuming()
    capture_thread.join()
    
    print('Finished Running')
    