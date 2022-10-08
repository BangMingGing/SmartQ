import os
import sys
import pika
import pickle
import time
import importlib

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

class Publisher():
    def __init__(self, header, exchange_name, routing_key):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.header = header
        self.exchange_name = exchange_name
        self.routing_key = routing_key


    def Publish(self, message):
        self.channel.basic_publish(
            exchange = self.exchange_name,
            routing_key = self.routing_key,
            body = pickle.dumps({'header' : self.header, 'message' : message})
        )



class IoT_Device():
    def __init__(self, device_name, exchange_name='input', routing_key=''):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.device_name = device_name
        self.queue_name = device_name

        # Queue 선언
        queue = self.channel.queue_declare(device_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=exchange_name, queue=device_name, routing_key=routing_key)

        self.publisher = Publisher(header='result', exchange_name='output', routing_key='toMongoDB')


    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')['message']
        task_name = message['task_name']
        contents = message['contents']

        dir_path = './TaskList'
        file_path = f'TaskList/{task_name}'
        module_path = file_path.replace('.py', '')
        module_path = module_path.replace('/', '.')

        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        with open(file_path, 'wb+') as f:
            f.write(contents)

        result_message = {}
        result_message['device_name'] = self.device_name
        result_message['task_name'] = task_name

        Task_Module = importlib.import_module(module_path)
        Task_Worker = Task_Module.Task()
        start_time = time.time()
        result_message['result'] = Task_Worker.work()
        result_message['work_time'] = time.time() - start_time

        print('result : ', result_message)

        self.publisher.Publish(result_message)
        # os.remove(file_path)

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print(f'[{self.device_name}] Start Consuming')
        self.channel.start_consuming()



class MongoDB():
    def __init__(self, queue_name='MongoDB', exchange_name='output', routing_key='toMongoDB'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = queue_name

        import MongoDB
        self.DB = MongoDB.DB()

        # Queue 선언
        queue = self.channel.queue_declare(queue_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)


    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')['message']

        # DB에 저장하는 코드
        self.DB.save_data(message)
        print(f'[MongoDB] message : {message}')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    
    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[MongoDB] Start Consuming')
        self.channel.start_consuming()



if __name__ == '__main__':

    FAST_API_SERVER_URL = '203.255.57.129:8000'
    RABBITMQ_SERVER_IP = '203.255.57.129'
    RABBITMQ_SERVER_PORT = '5672'
    
    run_process = sys.argv[1]

    message = {'message' : 'hello'}

    if run_process == 'Publish':
        process = Publisher(header='task', exchange_name='input', routing_key='')
        message = 'file'
        process.Publish(message)

    elif run_process == 'MongoDB':
        process = MongoDB()
        process.Consume()

    else:
        process = IoT_Device(device_name=run_process)
        process.Consume()

    
