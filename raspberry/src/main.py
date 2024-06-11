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
        sleep(2)


def ring_buzzer():
    global buzzer
    buzzer_time = 2
    
    buzzer.on()
    sleep(buzzer_time)
    buzzer.off()


def poll_buzzer():
    current_speed_limit = 20
    
    while(True):
        # consume from mqtt
        # update speed limit
        
        # check curr speed > speed limit
        # if yes, ring_buzzer()
        
        sleep(1)


if __name__ == '__main__':
    capture_thread = Thread(target=poll_camera_capture)
    buzzer_thread = Thread(target=poll_buzzer)
    
    capture_thread.start()
    buzzer_thread.start()
    
    print("Running")
    
    buzzer_thread.join()
    capture_thread.join()
    
    print('Finished')
    