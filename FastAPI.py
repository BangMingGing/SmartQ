from fastapi import FastAPI, File, UploadFile
from typing import List
import os
import SmartQ
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


app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {'item_id' : item_id}

@app.post("/file")
async def create_files(files: List[bytes] = File(...)):
    return {"file_size" : [len(file) for file in files]}

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