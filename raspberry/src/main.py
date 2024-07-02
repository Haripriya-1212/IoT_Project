import pika, sys, os, serial
from queue import Queue
from threading import Thread, Lock
from time import sleep
from io import BytesIO

from dotenv import load_dotenv

from picamera import PiCamera
from gpiozero import Buzzer

load_dotenv()

def main():
    speed_limit = 40
    speed_lock = Lock()

    test_lock = Lock()
    
    buzzer = Buzzer(17)
    buzzer.off()
    
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

        camera = PiCamera()
        camera.start_preview()

        sleep(2)
        print("Stared polling Camera Capture")

        while(True):
            capture_stream = BytesIO()
            camera.capture(capture_stream, 'jpeg')
            capture_stream.seek(0)

            with test_lock:
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
        

    def speed_callback(ch, method, properties, body):
        nonlocal channel, speed_limit
        
        speed_lim_val = int(body)

        with speed_lock:
            speed_limit = speed_lim_val
            print(f"Speed Limit Updated: {speed_limit}")
       
       
    def check_speed():
        nonlocal speed_limit

        spd = 20
        
        ser = serial.Serial("/dev/serial0")
        
        while True:
            sleep(1)
            spd = spd + 0.2
            test = True

            data = (str)(ser.readline())
            GPRMC_data = data.find('$GPRMC,')

            if(GPRMC_data > 0):
                knots = data.split(',')[7]
                # current_speed = float(knots) * 1.852

                print(f"Current Speed: {spd}")
                with speed_lock:
                    if spd > speed_limit and test:
                        print("Ringing buzzer")
                        ring_buzzer()

                        with test_lock:
                            channel.basic_publish(exchange='', routing_key='report', body=f'Speeding Found! Going at {spd} KM/H. Speed Limit is {speed_limit} KM/H')

                        test = False


    channel.basic_consume(queue='speed', on_message_callback=speed_callback, auto_ack=True)

    thread = Thread(target=poll_camera_capture)
    cs_thread = Thread(target=check_speed)
    
    thread.start()
    cs_thread.start()

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