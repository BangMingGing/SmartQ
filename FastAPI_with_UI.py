import base64
import glob
import string
from typing import List

import cv2
import motor.motor_asyncio
import pika
import uvicorn
import numpy as np
from bson import ObjectId
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, HTMLResponse
from pydantic import BaseModel, Field

import SmartQ



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


class InferenceRequest(BaseModel):
    image: str 
    model_names: List[str]



templates = Jinja2Templates(directory="html")
app = FastAPI()


@app.get("/home")
async def home(request : Request):
    return templates.TemplateResponse("/home.html", {"request":request})

@app.get("/home/get_inference_page")
async def inference(request : Request):
    return templates.TemplateResponse("/inference.html", {"request":request})

@app.get("/home/get_search_result_page")
async def inference(request : Request):
    return templates.TemplateResponse("/searchresult.html", {"request":request})

@app.post("/home/get_custom_model_page")
async def inference(request : Request):
    return templates.TemplateResponse("/custommodel.html", {"request":request})



@app.post("/home/get_inference_page/inference_request", status_code=status.HTTP_200_OK)
async def inference_request(request: Request, req: InferenceRequest):

    req.image = req.image[req.image.find(',') + 1:]
    img = np.frombuffer(base64.b64decode(req.image), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    cv2.imwrite('images/inference_image.jpg', img)
    
    Publisher_image = SmartQ.Publisher('image', 'input', '')
    with open('images/inference_image.jpg', 'rb') as f:
        contents = f.read()
    message = {}
    message['task_name'] = 'inference_image.jpg'
    message['contents'] = contents
    Publisher_image.Publish(message)

    Publisher_model = SmartQ.Publisher('task', 'input', '')
    for model in req.model_names:
        with open(f'onnxfile/{model}.onnx', 'rb') as f:
            contents = f.read()
        message = {}
        message['task_name'] = f'{model}.onnx'
        message['contents'] = contents
        Publisher_model.Publish(message)


    return templates.TemplateResponse("/inference.html", {"request":request})



@app.get("/home/get_search_result_page/search_result/all", response_description="show all results", response_model=List[ResultModel])
async def search_all():
    results = await db['all_data'].find().to_list(1000)
    return results


@app.get("/searchresult/device_name/{device_name}", response_description="show device results", response_model=List[ResultModel])
async def search_device(device_name):
    results = await db["all_data"].find({"device_name" : device_name}).to_list(1000)
    return results
    

@app.get("/searchresult/model_name/{task_name}", response_description="show task_name results", response_model=List[ResultModel])
async def search_task_name(task_name):
    results = await db["all_data"].find({"model_name" : task_name}).to_list(1000)
    return results


    
@app.delete("/result/delete/all", response_description="delete all Device")
async def delete_all():
    delete_results = await db["all_data"].delete_many({})

    if delete_results.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Result not found")
