from pymongo import MongoClient

mongo_client= MongoClient("profile")
db = mongo_client["cse312"]

profile_pic = db ["profile_pics"]
profile_id= db["user_id"]
usernames = db["usernames"]
passwords = db["passwords"]
post_collection = db ["posts"]
img_id_collection= db["img_id"]

    
def get_next_id():
    id_object= img_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id'])+1
        img_id_collection.update_one({},{'$set': {'last_id': next_id}})
        return next_id
    else:
        img_id_collection.insert_one({'last_id':1})
        return 1

def create(img_dict):
    profile_pic.insert_one(img_dict)
    img_dict.pop("_id")

def list_all():
    all_img= profile_pic.find({},{"_id":0})
    imgs=list(all_img)
    for img in imgs:
        if "delete" in dict(img).keys():
            imgs.remove(img)
    return imgs

def retreive(id):
    img=profile_pic.find_one({"id":id},{"_id":0})
    if(img!= None):
        if "delete" not in dict(img).keys():
            return dict(img)
    return (None)

def create_post(post_dict):
    post_collection.insert_one(post_dict)
    post_dict.pop("_id")

def list_all_post():
    all_post= post_collection.find({},{"_id":0})
    posts=list(all_post)
    for post in posts:
        if "delete" in dict(post).keys():
            posts.remove(post)
    return posts

def retreive_post(id):
    post=post_collection.find_one({"id":id},{"_id":0})
    if(post!= None):
        if "delete" not in dict(post).keys():
            return dict(post)
    return (None)