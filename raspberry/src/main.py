from io import BytesIO
from time import sleep
from picamera import PiCamera
from threading import Thread

from gpiozero import Buzzer

buzzer = Buzzer(17)

def poll_camera_capture():
    capture_stream = BytesIO()
    camera = PiCamera()
    camera.start_preview()
    sleep(2)
    
    while(True):
        camera.capture(capture_stream, 'jpeg')
        sleep(2)
        # publish to rabbitmq


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
    