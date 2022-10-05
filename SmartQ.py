import sys
import pika
import pickle
import time
# from MongoDBtest import DB

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
        
        with open('Task.py', 'wb') as f:
            f.write(contents)

        result = {}
        result['device_name'] = self.device_name
        result['task_name'] = task_name

        import Task
        start_time = time()
        result['result'] = Task.work()
        result['work_time'] = time() - start_time

        print('result : ', result)

        self.publisher.Publish(pickle.dumps(result))

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[Drone] Start Consuming')
        self.channel.start_consuming()



class MongoDB():
    def __init__(self, queue_name='MongoDB', exchange_name='output', routing_key='toMongoDB'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = queue_name

        # Queue 선언
        queue = self.channel.queue_declare(queue_name)
        # Queue-Exchange Binding
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)


    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')['message']

        print(f'[MongoDB] message : {message}')
        # DB에 저장하는 코드

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

    
