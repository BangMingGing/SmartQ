import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
from pymongo import MongoClient
import motor.motor_asyncio

app = FastAPI()

MONGODB_URL = "mongodb+srv://mgcho:4145@cluster0.psfzyux.mongodb.net/bmk?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

db = client.bmk

class PyObjectId(ObjectId):
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


class DeviceModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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



@app.get(
    "/", response_description="List all Device", response_model=List[DeviceModel]
)
async def list_devices():
    Devices = await db["all_data"].find().to_list(1000)
    return Devices

@app.get(
    "/device/{device_name}", response_description="List all Device", response_model=List[DeviceModel]
)
async def find_devices(device_name):
    ManyDevices = await db["all_data"].find({"device_name" : device_name}).to_list(1000)
    return ManyDevices
    
@app.get(
    "/task/{task_name}", response_description="List all Device of task", response_model=List[DeviceModel]
)
async def find_tasks(task_name):
    ManyTasks = await db["all_data"].find({"task_name" : task_name}).to_list(1000)
    return ManyTasks
    
@app.get(
    "/{id}", response_description="Get a single device", response_model=DeviceModel
)
async def show_Device(id):
    if (Device := await db["all_data"].find_one({"_id" : PyObjectId(id)})) is not None:
        return Device

    raise HTTPException(status_code=404, detail=f"Device {id} not found")
    
@app.delete("/", response_description="Delete all Device")
async def delete_Device():
    delete_results = await db["all_data"].delete_many({})

    if delete_results.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Device not found")
    
@app.delete("/{id}", response_description="Delete a Device")
async def delete_Device(id):
    delete_result = await db["all_data"].delete_one({"_id": PyObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Device {id} not found")

