import os
import json
import pickle
import requests
from pymongo import MongoClient

class DB():
    def __init__(self):
        client = MongoClient('localhost',27017)
        db1 = client['db1']
        self.test_status = {"test_status" : 0}
        self.all_data = db1.all_data
        self.dv1 = db1.dv1
        self.dv2 = db1.dv2
        self.dv3 = db1.dv3
        self.spec = db1.spec
        self.dron_location_infor = db1.dron_location_infor
        self.all_data.delete_many({})
        self.dv1.delete_many({})
        self.dv2.delete_many({})
        self.dv3.delete_many({})
        self.spec.delete_many({})
        self.dron_location_infor.delete_many({})
    
    def isin(self, col, data):
        if isinstance(data, list):
            col.insert_many(data)
        else:
            col.insert_one(data)

    def duplicate_spec(self):
        for i in range(1,4):
            msg_map = {"test_status" : 1, 'device_num' : i,
                        'Spec_name' : f'{self.spec_data["Spec_name"]}' } 
            self.isin(self.all_data,msg_map)

    def select_Col(self, dvnum):
        n = dvnum['device_num']
        if n == 1 :
            dv = self.dv1
        elif n == 2:
            dv = self.dv2
        elif n == 3: 
            dv = self.dv3

        return dv

    def json_to_info(self, exp_data):
        test_info = json.loads(exp_data["json_file"])
        mapping_info = json.loads(exp_data["mapping_info"])
        location_info = json.loads(exp_data["location"])
        return test_info, mapping_info, location_info

    def insert_test_info(self, mapping_info, test_info):
        self.all_data.find_one_and_update(mapping_info, {"$push" : test_info}, upsert = True)
        self.all_data.find_one_and_update(mapping_info, {"$set" : self.test_status}, upsert=True)
        
    def save_spec(self, msg):
        self.spec_data = json.loads(msg)
        self.isin(self.spec, self.spec_data)
        self.duplicate_spec()

        return True

    def save_test_info(self, msg):
        exp_data = json.loads(msg)
        test_info, mapping_info, location_info = self.json_to_info(exp_data)
        self.insert_test_info(mapping_info, test_info)
        dvnum = self.all_data.find_one(self.test_status, {'device_num' })
        dv = self.select_Col(dvnum)
        dv.insert_many(self.all_data.find(self.test_status))
        self.all_data.delete_one(self.test_status)

        return True

    def insert_location(self,msg):
        exp_data = json.loads(msg)
        test_info, mapping_info, location_info = self.json_to_info(exp_data) 
        self.isin(self.dron_location_infor,location_info)
if __name__ == "__main__":        
    DB = DB()

    SERVER_URL = "http://localhost:5000/"

    def get_spec():
        result = requests.get(SERVER_URL + "Spec")
        return pickle.loads(result.content, encoding='bytes')

    def get_test():
        result = requests.get(SERVER_URL + "test")
        return pickle.loads(result.content, encoding='bytes')


    DB.save_spec(get_spec())
    DB.save_test_info(get_test())
    DB.insert_location(get_test())
