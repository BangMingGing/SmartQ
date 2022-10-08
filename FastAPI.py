from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import Response
from typing import List
import os
import SmartQ
import pika
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, Field
import motor.motor_asyncio

app = FastAPI()

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
    task_name: str = Field(...)
    result: dict[str,str] = Field(...)
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


@app.post("/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...)):
    Publisher = SmartQ.Publisher('task', 'input', '')
    for file in files:
        contents = await file.read()
        """
        with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as fp:
            fp.write(contents)
        print(file.filename)
        """
        message = {}
        message['task_name'] = file.filename
        message['contents'] = contents
        Publisher.Publish(message)

    return {"filenames": [file.filename for file in files]}


@app.get("/result/search/all", response_description="show all results", response_model=List[ResultModel])
async def list_results():
    results = await db['all_data'].find()
    return results


@app.get("/result/search/device/{device_name}", response_description="show device results", response_model=List[ResultModel])
async def find_devices(device_name):
    results = await db["all_data"].find({"device_name" : device_name})
    return results
    

@app.get("/result/search/task/{task_name}", response_description="show task_name results", response_model=List[ResultModel])
async def find_tasks(task_name):
    results = await db["all_data"].find({"task_name" : task_name})
    return results


    
@app.delete("/result/delete/all", response_description="delete all Device")
async def delete_Device():
    delete_results = await db["all_data"].delete_many({})

    if delete_results.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Result not found")
    

@app.delete("/result/delete/delete_id/{id}", response_description="delete a id result")
async def delete_Device(id):
    delete_result = await db["all_data"].delete_one({"_id": ResultID(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Result {id} not found")