import sys
import pika
import pickle
import requests
from MongoDBtest import DB


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
    def __init__(self, queue_name='Drone', publish_exchange_name='output', publish_routing_key='toMongoDB'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = queue_name

        self.publisher = Publisher(header='result', exchange_name=publish_exchange_name, routing_key=publish_routing_key)


    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')['message']

        with open('Specification.py', 'wb') as f:
            f.write(message['Specification'])

        result = self.tester(testing(message['Spec_Name']))
        # print(f'[Drone] message : {message}')

        self.publisher.Publish(pickle.dumps(result))

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[Drone] Start Consuming')
        self.channel.start_consuming()



class MongoDB():
    def __init__(self, queue_name='MongoDB'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = queue_name


    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')

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
        process = Publisher(header='spec', exchange_name='input', routing_key='')
        message = 'file'
        process.Publish(message)
    
    elif run_process == 'IoT Device':
        process = IoT_Device(queue_name='Drone', publish_exchange_name='output', publish_routing_key='toMongoDB')
        process.Consume()

    elif run_process == 'MongoDB':
        process = MongoDB(queue_name='MongoDB')
        process.Consume()

    
