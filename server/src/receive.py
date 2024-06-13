import pika, sys, os
from threading import Thread
from time import sleep
from dotenv import load_dotenv

load_dotenv()

def main():
    url = os.getenv("CLOUDAMQP_URL")
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='video')
    channel.queue_declare(queue='speed')
    channel.queue_declare(queue='report')


    def video_callback(ch, method, properties, body):
        print(f"Received Video Frame: {body}")

        # USE ML MODEL TO CHECK IF FRAME HAS SPEED SIGN
        # IF NO, RETURN

        # USE OPENCV TO EXTRACT SPEED LIMIT FROM FRAME AND PUBLISH IT
        channel.basic_publish(exchange='', routing_key='speed', body='80')


    def report_callback(ch, method, properties, body):
        print(f"Received Report: {body}")
        # USE EMAIL TO SEND REPORT TO EMAIL AND STORE IT IN DATABASE


    channel.basic_consume(queue='video', on_message_callback=video_callback, auto_ack=True)
    channel.basic_consume(queue='report', on_message_callback=report_callback, auto_ack=True)

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