import hashlib
import json
import secrets
# import bcrypt
import util.database as db
import util.usersDB as usersdb
from util.response import generate_response
from util.router import Route

def add_paths(router):

    router.add_route(Route("GET", "/users/.", login__))
    router.add_route(Route("PUT", "/users/.", update))
    router.add_route(Route("DELETE","/users/", delete))
    # router.add_route(Route("GET", "/login", login))

# def login(request, handler):
#     html = open("public/login.html","rb").read()
#     byteHTML = bytearray(html)
#     sizeHTML = len(byteHTML)
#     handler.request.sendall(("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nContent-Length: "+str(sizeHTML)+"\r\n\r\n").encode()+html)

def login__(request, handler):
    body_string =request.path
    id= body_string[7:]

    ret=db.retreive(int(id))
    if(ret==None):
        four_oh_four(handler)
    response= generate_response(json.dumps(ret).encode(), "application/json", "200 OK")
    handler.request.sendall(response)

def list_all(request, handler):
    response = generate_response(json.dumps(db.list_all()).encode(), "application/json", "200 OK")
    handler.request.sendall(response)

def update(request, handler):
    body_string =request.jason
    body_dict=json.loads(body_string)
    id=request.path[7:]

    ret=db.update(int(id),body_dict)
    if(ret==None):
        four_oh_four(handler)
    response= generate_response(json.dumps(ret).encode(), "application/json", "200 OK")
    handler.request.sendall(response)

def delete(request, handler):
    id=request.path[7:]
    ret=db.delete(int(id))
    if ret:
        handler.request.sendall(b"HTTP/1.1 204 No Content\r\nContent-Type: text/plain\r\nContent-Length: 32\r\n\r\nThe requested content is deleted")
    else: 
        four_oh_four(handler)

def four_oh_four(handler):
    handler.request.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 36\r\n\r\nThe requested content does not exist")
