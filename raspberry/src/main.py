from io import BytesIO
from time import sleep
from threading import Thread

# from picamera import PiCamera
# from gpiozero import Buzzer
from dotenv import load_dotenv

import pika
import os

load_dotenv()

# buzzer = Buzzer(17)
i = 1

def poll_camera_capture():
    global i, channel
    # capture_stream = BytesIO()
    # camera = PiCamera()
    # camera.start_preview()
    # sleep(2)
    print("stared polling camera capture")
    while(True):
        # camera.capture(capture_stream, 'jpeg')
        # capture_stream.seek(0)
        # channel.basic_publish(exchange='', routing_key='video', body=capture_stream.read())
        print(f"Published Frame: {i}")
        channel.basic_publish(exchange='', routing_key='video', body=f"[Video Frame Test] Count: {i}")
        i = i + 1
        sleep(1)


# def ring_buzzer():
#     global buzzer
#     buzzer_time = 2
    
#     buzzer.on()
#     sleep(buzzer_time)
#     buzzer.off()


current_speed = 20

def speed_callback(ch, method, properties, body):
    global current_speed
    
    speed_limit = int(body)

    print("Received Speed Limit")
    print(speed_limit)

    current_speed += 1

    if current_speed > speed_limit:
        # ring_buzzer()
        channel.basic_publish(exchange='', routing_key='report', body='Speeding Found!')
        current_speed = 0


# RabbitMQ Setup

def on_channel_open(chn):
    global channel, capture_thread

    channel = chn

    chn.queue_declare(queue='video')
    chn.queue_declare(queue='speed')
    chn.queue_declare(queue='report')

    chn.basic_consume(queue='speed', on_message_callback=speed_callback, auto_ack=True)

    capture_thread = Thread(target=poll_camera_capture)
    capture_thread.start()


def on_close(connection):
    global capture_thread
    capture_thread.join()


def on_open(connection):
    connection.channel(on_open_callback=on_channel_open)
    connection.add_on_close_callback(on_close)


url = os.getenv("CLOUDAMQP_URL")
# params = pika.URLParameters(url)
params = pika.ConnectionParameters('localhost')
connection = pika.SelectConnection(params, on_open_callback=on_open)
channel = None
capture_thread = None


if __name__ == '__main__':
    try:
        print("Running PiSpeedCam Server Thread!")
        connection.ioloop.start()
    except KeyboardInterrupt:
        print('Finished Running')
        connection.close()
