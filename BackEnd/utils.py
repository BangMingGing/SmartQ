import pika
import pickle
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List

RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

# Publisher send messages node to node, it used in FastAPI(send image, model to Deivce), Device(send inference result to DB)
class Publisher():
    def __init__(self, header, exchange_name, routing_key):
        self.credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', self.credentials))
        self.channel = self.connection.channel()

        self.header = header
        self.exchange_name = exchange_name
        self.routing_key = routing_key


    def publish(self, message):
        self.channel.basic_publish(
            exchange = self.exchange_name,
            routing_key = self.routing_key,
            body = pickle.dumps({'header' : self.header, 'message' : message})
        )


# Request Modele of Inference's image file and model names
class InferenceRequest(BaseModel):
    image: str 
    model_names: List[str]

# Request Model of Custom Model's onnx file and model name
class CustomModelRequest(BaseModel):
    onnx: str
    custom_model_name: str
