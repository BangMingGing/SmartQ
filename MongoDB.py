from pymongo import MongoClient

class DB():
    def __init__(self):
        client = MongoClient("mongodb+srv://mgcho:4145@cluster0.psfzyux.mongodb.net/test")
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
