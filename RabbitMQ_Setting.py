
import pika

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', credentials))
channel = connection.channel()


# input Exchange 선언
channel.exchange_declare(exchange='input', exchange_type='fanout')

# output Exchange 선언
channel.exchange_declare(exchange='output', exchange_type='direct')



# IoT_Device1 Queue 선언
queue = channel.queue_declare('IoT_Device1')

# MongoDB Queue 선언
queue = channel.queue_declare('MongoDB')



# (IoT_Device1 Queue - input Exchange) Binding
channel.queue_bind(exchange='input', queue="IoT_Device1", routing_key='toIoT_Device1')



# (MongoDB Queue - output Exchange) Binding
channel.queue_bind(exchange='output', queue="MongoDB", routing_key='toMongoDB')