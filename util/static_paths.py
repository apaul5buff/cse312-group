from util.router import Route
from util.response import generate_response
from util.response import *
from util.templete_engine import render_templete
import util.chatdata as db
import secrets
from util.request import *

def add_paths(router):
    router.add_route(Route('GET', '/hi', hi)) 
    router.add_route(Route('GET', '/hello', hello))
    router.add_route(Route('GET',"/functions.js", js))
    router.add_route(Route('GET', "/style.css", style))
    router.add_route(Route('GET',"/image/.", images))
    router.add_route(Route('POST', "/register", registration))
    router.add_route(Route('POST', "/imageupload", imageupload))
    router.add_route(Route('GET', "/$", home))

def home(request, handler):
    posts=db.list_all_post()
    img=db.list_all()
    token=secrets.token_urlsafe(16)
    db.add_token(token)

    templated_homepage = render_templete(handler.images)
    # content= render_homepage("public/index.html",{"image_name": "Eagle!",
    # "image_filename":"parrot.jpg", "loop_data":posts, "loop_img":img, "token":token})
    # print(f"Templated homepage data: {templated_homepage}")
    response=generate_response(templated_homepage.encode())
    print(f"Templated HTML response: {response}")
    handler.request.sendall(response)
    
    # send_file("public/index.html", "text/html; charset=utf-8", request, handler)

def js(request, handler):
    send_file("functions.js", "text/javascript; charset=utf-8", request, handler)

def style(request, handler):
    send_file("style.css", "text/css; charset=utf-8", request, handler)

def images(request, handler):
    path_prefix= '/image/'
    image_name = request.path[request.path.find(path_prefix)+len(path_prefix):]
    image_name = image_name.replace("/","")
    send_file("image/"+ image_name, "image/jpeg", request, handler)

def send_file(filename, mime_type, request, handler):
    with open(filename, "rb") as content:
        body=content.read()
        response= generate_response(body, mime_type, '200 OK')
        handler.request.sendall(response)

def registration(request, handler):
    print(request.body)
    response= generate_response("WORKED".enocode(),"text/plain", response, handler)
    handler.request.sendall(response)

def imageupload(request, handler):
    parse_multipart(request)
    new_file_name = "./image/image%d.jpg" % len(handler.images)
    handler.images.append(new_file_name)
    
    with open(new_file_name, "wb") as content:
        content.write(request.parts["image"])
        
    # print(handler.images)
    response = redirect("/")

    handler.request.sendall(response)

def hello(request, handler):  
    send_file("hello.txt", "text/plain; charset=utf-8",request, handler)
    
def hi(request,handler):
    handler.request.sendall(b"HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /hello\r\n\r\n")
  
