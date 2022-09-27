
import pika

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, credentials))
channel = connection.channel()


# input Exchange 선언
channel.exchange_declare(exchange='input', exchange_type='fanout')

# output Exchange 선언
channel.exchange_declare(exchange='output', exchange_type='direct')



# Drone Queue 선언
queue = channel.queue_declare('Drone')

# Server Queue 선언
queue = channel.queue_declare('Server')

# MongoDB Queue 선언
queue = channel.queue_declare('MongoDB')



# (Drone Queue - input Exchange) Binding
channel.queue_bind(exchange='input', queue="Drone", routing_key='toDrone')

# (Server Queue - input Exchange) Binding
channel.queue_bind(exchange='input', queue="Server", routing_key='toServer')

# (MongoDB Queue - input Exchange) Binding
channel.queue_bind(exchange='input', queue="MongoDB", routing_key='toMongoDB')



# (MongoDB Queue - output Exchange) Binding
channel.queue_bind(exchange='output', queue="MongoDB", routing_key='toMongoDB')