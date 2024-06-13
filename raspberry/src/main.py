import pika, sys, os
from threading import Thread
from time import sleep
from io import BytesIO

from dotenv import load_dotenv

from picamera import PiCamera
from gpiozero import Buzzer

load_dotenv()

def main():
    buzzer = Buzzer(17)
    
    url = os.getenv("CLOUDAMQP_URL")
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='video')
    channel.queue_declare(queue='speed')
    channel.queue_declare(queue='report')

    i = 1
    def poll_camera_capture():
        nonlocal i, channel

        capture_stream = BytesIO()
        camera = PiCamera()
        camera.start_preview()

        sleep(2)
        print("Stared polling Camera Capture")

        while(True):
            camera.capture(capture_stream, 'jpeg')
            capture_stream.seek(0)
            channel.basic_publish(exchange='', routing_key='video', body=capture_stream.read())
            print(f"Published Frame: {i}")
            i = i + 1
            sleep(1)


    def ring_buzzer():
        nonlocal buzzer
        buzzer_time = 4
        
        buzzer.on()
        sleep(buzzer_time)
        buzzer.off()
        
    # REMOVE THIS LINE WHEN GPS IS IMPLEMENTED
    current_speed = 20

    def speed_callback(ch, method, properties, body):
        nonlocal current_speed, channel
        
        speed_limit = int(body)
        print(f"Received Speed Limit: {speed_limit}")

        # GET CURRENT SPEED FROM GPS HERE INSTEAD AND JUST ASSIGN IT TO current_speed
        current_speed += 1

        if current_speed > speed_limit:
            ring_buzzer()
            channel.basic_publish(exchange='', routing_key='report', body='Speeding Found!')
            current_speed = 0 # REMOVE THIS LINE WHEN GPS IS IMPLEMENTED


    channel.basic_consume(queue='speed', on_message_callback=speed_callback, auto_ack=True)

    thread = Thread(target=poll_camera_capture)
    thread.start()

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)