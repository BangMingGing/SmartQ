from pymongo import MongoClient

MONGODB_SERVER_IP = '203.255.57.129'
MONGODB_SERVER_PORT = 27017

class DB():
    def __init__(self):
        client = MongoClient(MONGODB_SERVER_IP, MONGODB_SERVER_PORT)
        db1 = client['bmk']
        self.all_data = db1.all_data
        self.all_data.delete_many({})
    
    def isin(self, col, data):
        if isinstance(data, list):
            col.insert_many(data)
        else:
            col.insert_one(data)

    def save_data(self,msg):
        self.isin(self.all_data, msg)


if __name__ == "__main__":        
    DB = DB()

    msg = {
        "header" : "Spec",
        "device_name" : "device_name",
        "task_name" : "task_name",
        "result" : "result",
        "work_time" : "work_time"

    }

    DB.__init__()
    DB.save_data(msg)
