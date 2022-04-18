from pymongo import MongoClient

mongo_client= MongoClient("mongo")
db = mongo_client["cse312"]

users_collection = db ["users"]
users_id_collection= db["users_id"]

def get_next_id():
    id_object= users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id'])+1
        users_id_collection.update_one({},{'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id':1})
        return 1

def create(user_dict):
    users_collection.insert_one(user_dict)
    user_dict.pop("_id")

def list_all():
    all_users= users_collection.find({},{"_id":0})
    users=list(all_users)
    for user in users:
        if "delete" in dict(user).keys():
            users.remove(user)
    return users

def retreive(id):
    user=users_collection.find_one({"id":id},{"_id":0})
    if(user!= None):
        if "delete" not in dict(user).keys():
            return dict(user)
    return (None)

def update(id,user_dict):
    user=users_collection.find_one({"id":id},{"_id":0})
    if(user!= None):
        if "delete" not in dict(user).keys():
            users_collection.update_one({"id":id},{"$set": user_dict})
            return(dict(users_collection.find_one({"id":id},{"_id":0})))
    return (None)


def delete(id):
    user=users_collection.find_one({"id":id})
    if(user!= None):
        if "delete" not in dict(user).keys():
            users_collection.update_one({"id":id},{"$set": {"delete":True}})
            return(True)
    return (False)
