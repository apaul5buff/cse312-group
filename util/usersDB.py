from pymongo import MongoClient

mongo_client= MongoClient("users")
db = mongo_client["cse312"]

users = db["users"]
chatlogs = db["chatlog"]

def createAccount(userDict):
    users.insert_one(userDict)
    userDict.pop('_id')      

def userLookup(auth):
    user = users.distinct("username",{"auth":auth})
    if len(user) >0:
        return user[0]  
    else:
        return False

def add_auth(username,auth):
    hashed_auth_token= {"auth":auth}
    users.update_one({"username":username}, {"$set":hashed_auth_token})
    
def retrieve_salt(username):
    salt = users.distinct("salt",{"username":username})
    return salt[0]
    
def retrieve_hash(username):
    salt = users.distinct("hash",{"username":username})
    return salt[0]

def repeat_username_check(username):
    usercheck = list(users.find({"username":username}))
    if len(usercheck) >0:
        return True
    else:
        return False

def createLog(chatlog):
    chatlogs.insert_one(chatlog)
    chatlog.pop('_id') 

def chat():
    chat = chatlogs.find({},{"_id":0})
    return list(chat)

def addXSRF(xsrf,username):
    XSRF = {"xsrf":xsrf}
    users.update_one({"username":username},{"$set":XSRF})

def checkXSRF(username,xsrf):
    check = list(users.find({"xsrf":xsrf,"username":username}))
    if len(check) >0:
        return True
    else:
        return False

def add_fav(username,fav):
    FAV= {"fav_prof":fav}
    users.update_one({"username":username}, {"$set":FAV})
    
def fav_prof_lookup(username):
    fav = users.distinct("fav_prof",{"username":username})
    if len(fav) >0:
        return fav[0]  
    else:
        return False