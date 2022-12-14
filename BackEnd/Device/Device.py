import os
import sys
import pika
import pickle
import time
import subprocess

sys.path.append('..')
import utils as ut

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

test_start = 0
test_end = 0

class Device():
    
    def __init__(self, device_name, exchange_name='input', routing_key=''):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters \
            (RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.device_name = device_name
        self.queue_name = device_name
        
        # Queue 선언
        queue = self.channel.queue_declare(device_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=exchange_name, queue=device_name, routing_key=routing_key)

        self.publisher = ut.Publisher(header='result', exchange_name='output', routing_key='toMongoDB')


    
    def callback(self, ch, method, properties, body):
        global test_end
        global test_start
        test_end = time.time()
        print('total_time : ', test_end - test_start)
        msg = pickle.loads(body, encoding='bytes')
        header = msg['header']
        message = msg['message']
        model_name = message['model_name']
        contents = message['contents']

        if header == 'model':
            with open(f'{model_name}', 'wb') as f:
                f.write(contents)

            model = ['python', 'Inference_worker.py', model_name, 'inference_image.jpg']

            result_message = {}
            result_message['device_name'] = self.device_name
            result_message['model_name'] = model_name

            start_time = time.time()
            try:
                results = subprocess.check_output(model, shell=False, encoding='UTF-8')
            except Exception:
                result_message['error'] = Exception
            result_message['work_time'] = time.time() - start_time

            tmp = results.split('^')
            result_message[tmp[0]] = tmp[1]
            result_message[tmp[2]] = tmp[3]

            print('result : ', result_message)

            self.publisher.publish(result_message)
            os.remove(f'{model_name}')

        elif header == 'image':
            with open('inference_image.jpg', 'wb') as f:
                f.write(contents)
            print("image saved")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        
        test_start = time.time()

    def consume(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print(f'[{self.device_name}] Start Consuming')
        self.channel.start_consuming()



if __name__ == '__main__':
    
    run_process = sys.argv[1]

    process = Device(device_name=run_process)
    process.consume()

    
