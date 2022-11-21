import sys
import pika
import pickle
from pymongo import MongoClient

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

MONGODB_SERVER_IP = '203.255.57.129'
MONGODB_SERVER_PORT = 27017


class MongoDB():
    def __init__(self, queue_name='MongoDB', exchange_name='output', routing_key='toMongoDB'):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.queue_name = queue_name

        queue = self.channel.queue_declare(queue_name)
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

        # MongoDB
        client = MongoClient(MONGODB_SERVER_IP, MONGODB_SERVER_PORT)
        db1 = client['bmk']
        self.all_data = db1.all_data


    def save_data(self,msg):
        col = self.all_data
        data = msg
        if isinstance(data, list):
            col.insert_many(data)
        else:
            col.insert_one(data)

    
    def callback(self, ch, method, properties, body):
        message = pickle.loads(body, encoding='bytes')['message']

        # DB에 저장하는 코드
        self.save_data(message)
        print(f'[MongoDB] message : {message}')

        ch.basic_ack(delivery_tag=method.delivery_tag)

    
    def Consume(self):
        self.channel.basic_consume(on_message_callback=self.callback, queue=self.queue_name)
        print('[MongoDB] Start Consuming')
        self.channel.start_consuming()



if __name__ == '__main__':
    
    run_process = sys.argv[1]

    process = MongoDB()
    process.Consume()


    
