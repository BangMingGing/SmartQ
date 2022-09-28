import os
import json
import pickle
import requests
from pymongo import MongoClient

class DB():
    def __init__(self):
        client = MongoClient('localhost',27017)
        db1 = client['db1']
        self.all_data = db1.all_data
        self.all_data.delete_many({})
        
    def isin(self, col, data):
        if isinstance(data, list):
            col.insert_many(data)
        else:
            col.insert_one(data)
            
    def json_to_info(self, exp_data):
        test_info = json.loads(exp_data["json_file"])
        return test_info

    def insert_test_info(self, test_info):
        self.all_data.find_one_and_update(mapping_info, {"$push" : test_info}, upsert = True)
       
    def save_test_info(self, msg):
        exp_data = json.loads(msg)
        test_info = self.json_to_info(exp_data)
        self.insert_test_info(test_info)
        dv.insert_many(self.all_data.find(self.test_status))
        return True
        
if __name__ == "__main__":        
    DB = DB()

    SERVER_URL = "http://localhost:5000/"

    def get_test():
        result = requests.get(SERVER_URL + "test")
        return pickle.loads(result.content, encoding='bytes')

    DB.save_test_info(get_test())
