import base64
import cv2
import glob
import motor.motor_asyncio
import pika
import numpy as np
from fastapi import FastAPI, status, Request
from fastapi.templating import Jinja2Templates
from typing import List
import utils as ut

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

templates = Jinja2Templates(directory="../FrontEnd")
app = FastAPI()

@app.get("/home")
async def home_page(request : Request):
    context = {'request': request}
    return templates.TemplateResponse("/home.html", context)

@app.get("/home/get_inference_page")
async def inference_page(request : Request):
    model_path = glob.glob('../onnxfile/*.onnx')
    model_names = []
    for model in model_path:
        model_tmp = model.replace('../onnxfile/', '')
        model_name = model_tmp.replace('.onnx', '')
        model_names.append(model_name)
        print(model_name)
    context = {'request': request, 'model_names': model_names}
    return templates.TemplateResponse("/inference.html", context)

@app.get("/home/get_search_result_page")
async def search_result_page(request : Request):
    context = {'request': request}
    return templates.TemplateResponse("/searchresult.html", context)

@app.get("/home/get_custom_model_page")
async def custom_model_page(request : Request):
    context = {'request': request}
    return templates.TemplateResponse("/custommodel.html", context)

@app.post("/home/get_inference_page/inference_request", status_code=status.HTTP_200_OK)
async def inference_request(request: Request, req: ut.InferenceRequest):

    # save_image(req.image)
    req.image = req.image[req.image.find(',') + 1:]
    img = np.frombuffer(base64.b64decode(req.image), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    cv2.imwrite('../images/inference_image.jpg', img)
    
    # publish_image()
    Publisher_image = ut.Publisher('image', 'input', '')
    with open('../images/inference_image.jpg', 'rb') as f:
        contents = f.read()
    message = {}
    message['model_name'] = 'inference_image.jpg'
    message['contents'] = contents
    Publisher_image.publish(message)

    # publish_model()
    Publisher_model = ut.Publisher('model', 'input', '')
    for model in req.model_names:
        with open(f'../onnxfile/{model}.onnx', 'rb') as f:
            contents = f.read()
        message = {}
        message['model_name'] = f'{model}.onnx'
        message['contents'] = contents
        Publisher_model.publish(message)

    context = {'request': request}
    return templates.TemplateResponse("/inference.html", context)

@app.post("/home/get_custom_model_page/save_custom_model", status_code=status.HTTP_200_OK)
async def save_custom_model(request: Request, req: ut.CustomModelRequest):
    print(req.custom_model_name)
    
    req.onnx = req.onnx[req.onnx.find(',') + 1:]
    print(req.onnx[:100])
    model = np.frombuffer(base64.b64decode(req.onnx), np.uint8)
    with open(f'../onnxfile/{req.custom_model_name}.onnx', 'wb') as f:
        f.write(model)

    context = {'request': request}
    return templates.TemplateResponse("/custommodel.html", context)

@app.get("/home/get_search_result_page/search_result/all", response_description="show all results", response_model=List[ut.ResultModel])
async def search_all():
    results = await db['all_data'].find().to_list(1000)
    return results


@app.get("/searchresult/device_name/{device_name}", response_description="show device_name results", response_model=List[ut.ResultModel])
async def search_device_name(device_name):
    results = await db["all_data"].find({"device_name" : device_name}).to_list(1000)
    return results
    

@app.get("/searchresult/model_name/{model_name}", response_description="show model_name results", response_model=List[ut.ResultModel])
async def search_model_name(model_name):
    results = await db["all_data"].find({"model_name" : model_name}).to_list(1000)
    return results
    
@app.delete("/result/delete/all", response_description="delete all Device")
async def delete_all():
    delete_results = await db["all_data"].delete_many({})
    return delete_results
