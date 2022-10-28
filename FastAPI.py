from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import Response
from typing import List
import glob
import SmartQ
import pika
from bson import ObjectId
from pydantic import BaseModel, Field
import motor.motor_asyncio

# RabbitMQ
RABBITMQ_SERVER_IP = '203.255.57.129'
RABBITMQ_SERVER_PORT = '5672'

credentials = pika.PlainCredentials('rabbitmq', '1q2w3e4r')
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER_IP, RABBITMQ_SERVER_PORT, 'vhost', credentials))
channel = connection.channel()

channel.exchange_declare(exchange='input', exchange_type='fanout')
channel.exchange_declare(exchange='output', exchange_type='direct')


# MongoDB
MONGODB_SERVER_IP = '203.255.57.129'
MONGODB_SERVER_PORT = 27017

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_SERVER_IP, MONGODB_SERVER_PORT)
db = client['bmk']

# default onnx file
default_files = glob.glob('onnxfile/*.onnx')
# print(default_files)

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

class Model_names(BaseModel):
    model_names: List[str]


class ResultModel(BaseModel):
    id: ResultID = Field(default_factory=ResultID, alias="_id")
    device_name: str = Field(...)
    task_name: str = Field(...)
    result: str = Field(...)
    work_time: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "device_name": "drone",
                "task_name": "drone information",
                "result": {"location" : "123.123.123", "altitude" : "123", "longtitude" : "345"},
                "work_time": "1.234",
            }
        }

app = FastAPI()


@app.post("/upload/upload_image")
async def upload_images(files: List[UploadFile] = File(...)):
    Publisher = SmartQ.Publisher('image', 'input', '')
    for file in files:
        contents = await file.read()
        message = {}
        message['task_name'] = file.filename
        message['contents'] = contents
        Publisher.Publish(message)

    return {"filenames": [file.filename for file in files]}


@app.post("/upload/select_model", description='resent18, densenet121, inception_v3')
async def with_default_model(Model_names: Model_names):
    
    Publisher = SmartQ.Publisher('task', 'input', '')
    for model in Model_names:
        with open(f'onnxfile/{model}.onnx', 'rb') as f:
            contents = f.read()
        message = {}
        message['task_name'] = f'{model}.onnx'
        message['contents'] = contents
        Publisher.Publish(message)

    return {"filenames": default_files}



@app.get("/result/search/all", response_description="show all results", response_model=List[ResultModel])
async def search_all():
    results = await db['all_data'].find().to_list(1000)
    return results

    
@app.delete("/result/delete/all", response_description="delete all Device")
async def delete_all():
    delete_results = await db["all_data"].delete_many({})

    if delete_results.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Result not found")
