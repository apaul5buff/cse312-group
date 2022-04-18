
import json
import util.database as db
from util.response import generate_response
from util.router import Route

def add_paths(router):
    router.add_route(Route('POST', '/user', create))
    router.add_route(Route('GET', '/users/.', retrieve))
    router.add_route(Route('GET', '/users', list_all))
    router.add_route(Route('PUT', '/users/.', update))
    router.add_route(Route('DELETE','/users/', delete))


def create(request, handler):
    body_string =request.body.decode()
    body_dict=json.loads(body_string)
    body_dict['id']= db.get_next_id()

    db.create(body_dict)

    response = generate_response(json.dumps(body_dict).encode(), 'application/json', '201 Created')
    handler.request.sendall(response)

def list_all(request, handler):
    response = generate_response(json.dumps(db.list_all()).encode(), 'application/json', "200 OK")
    handler.request.sendall(response)

def retrieve(request, handler):
    body_string =request.path
    id= body_string[7:]

    ret=db.retreive(int(id))
    if(ret==None):
        four_oh_four(handler)
    response= generate_response(json.dumps(ret).encode(), 'application/json', "200 OK")
    handler.request.sendall(response)

def update(request, handler):
    body_string =request.jason
    body_dict=json.loads(body_string)
    id=request.path[7:]

    ret=db.update(int(id),body_dict)
    if(ret==None):
        four_oh_four(handler)
    response= generate_response(json.dumps(ret).encode(), 'application/json', "200 OK")
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
