import pika
import pickle

from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List

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


    def publish(self, message):
        self.channel.basic_publish(
            exchange = self.exchange_name,
            routing_key = self.routing_key,
            body = pickle.dumps({'header' : self.header, 'message' : message})
        )


class ResultID(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ResultModel(BaseModel):
    id: ResultID = Field(default_factory=ResultID, alias="_id")
    device_name: str = Field(...)
    model_name: str = Field(...)
    result: str = Field(...)
    work_time: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "device_name": "drone",
                "model_name": "drone information",
                "result": {"location" : "123.123.123", "altitude" : "123", "longtitude" : "345"},
                "work_time": "1.234",
            }
        }


class InferenceRequest(BaseModel):
    image: str 
    model_names: List[str]


class CustomModelRequest(BaseModel):
    onnx: str
    custom_model_name: str