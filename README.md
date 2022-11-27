# OffloadingDrone
소개론 8조


1. [Server] RabbitMQ Server start : sudo service rabbitmq-server start
2. [Server] MongoDB Server start : mongod --dbpath ~/data/db --bind_ip 0.0.0.0
3. [Server] FastAPI Server start : uvicorn FastAPI:app --reload --host=0.0.0.0 --port=8001
3. [Server] SmartQ MongoDB execute : python MongoDB.py
4. [Device] SmartQ Device execute : python Device.py <"My Device">
5. Go to "ServerIP:FastAPI_Port/home"
6. You can upload your task files
7. You can see results 
