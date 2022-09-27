from asyncio import QueueEmpty
import queue
import sys
import pika
import json
import pickle


class Publisher():
    def __init__(self, exchange_name, routing_key):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.exchange_name = exchange_name
        self.routing_key = routing_key


    def Publish(self, message):
        self.channel.basic_publish(
            exchange = self.exchange_name,
            routing_key = self.routing_key,
            body = pickle.dumps(message)
        )



class Drone():
    def __init__(self, queue_name='Drone', publish_exchange_name='output', publish_routing_key='toMongoDB'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.publisher = Publisher(exchange_name=publish_exchange_name, routing_key=publish_routing_key)

        self.queue_name = queue_name
        

    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')

        print(f'[Drone] message : {message}')

        self.publisher.Publish(pickle.dumps(message))

        ch.basic_ack(delivery_tag=method.delivery_tag)


    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[Drone] Start Consuming')
        self.channel.start_consuming()



class Server():
    def __init__(self, queue_name='Server'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = queue_name

    
    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')

        print(f'[Server] message : {message}')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    
    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[Server] Start Consuming')
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

        ch.basic_ack(delivery_tag=method.delivery_tag)

    
    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[MongoDB] Start Consuming')
        self.channel.start_consuming()



if __name__ == '__main__':

    RABBITMQ_SERVER_IP = '203.255.57.129'
    RABBITMQ_SERVER_PORT = '5672'
    
    run_process = sys.argv[1]

    message = 'hello'

    if run_process == 'Publish':
        process = Publisher(exchange_name='input', routing_key='')
        process.Publish(message)
    
    elif run_process == 'Drone':
        process = Drone(queue_name='Drone', publish_exchange_name='output', publish_routing_key='toMongoDB')
        process.Consume()
        
    elif run_process == 'Server':
        process = Server(queue_name='Server')
        process.Consume()

    elif run_process == 'MongoDB':
        process = MongoDB(queue_name='MongoDB')
        process.Consume()

    
