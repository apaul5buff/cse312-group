from pymongo import MongoClient

mongo_client= MongoClient("ws")
db = mongo_client["cse312"]

ws_collection = db ["ws"]
ws_id_collection= db["ws_id"]

def get_next_id():
    id_object= ws_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id'])+1
        ws_id_collection.update_one({},{'$set': {'last_id': next_id}})
        return next_id
    else:
        ws_id_collection.insert_one({'last_id':1})
        return 1

def create(user_dict):
    ws_collection.insert_one(user_dict)
    user_dict.pop("_id")

def list_all():
    all_users= ws_collection.find({},{"_id":0})
    return list(all_users)




