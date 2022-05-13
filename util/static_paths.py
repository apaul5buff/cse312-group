import hashlib
from urllib.request import Request
from util.request import parse_multipart
from util.router import Route
from util.response import generate_response, redirect
from util.templete_engine import render_image, render_template
import util.chatdata as db
import util.usersDB as usersdb
import secrets
import bcrypt
import json


def add_paths(router):
    router.add_route(Route('GET',"/functions.js", js))
    router.add_route(Route('GET', "/style.css", style))
    router.add_route(Route('GET',"/image/.", images))
    router.add_route(Route('POST', "/imageupload", imageupload))
    router.add_route(Route('GET', "/$", home))
    router.add_route(Route("POST", "/register", registration))
    router.add_route(Route("POST", "/", newlogin))    
    router.add_route(Route("GET", "/register", registered))
    router.add_route(Route("GET", "/login", login))
    router.add_route(Route("POST", "/fav_prof", add_prof))
    router.add_route(Route("GET", "/imageupload", image))

    router.add_route(Route('POST', "/vote", vote))

def image(request, handler):

    token=secrets.token_urlsafe(16)
    db.add_token(token)

    templated_homepage = render_image(handler.images)

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








def imageupload(request, handler):
    parse_multipart(request)
    new_file_name = "./image/image%d.jpg" % len(handler.images)
    handler.images.append(new_file_name)
    
    with open(new_file_name, "wb") as content:
        content.write(request.parts["image"])
        
    # print(handler.images)
    response = redirect("/imageupload")

    handler.request.sendall(response)


def vote(request, handler):
    parse_multipart(request)
    new_file_name = "./image/image%d.jpg" % len(handler.images)
    handler.images.append(new_file_name)

    with open(new_file_name, "wb") as content:
        content.write(request.parts["image"])

    # print(handler.images)
    response = redirect("/vote")

    handler.request.sendall(response)







def hello(request, handler):  
    send_file("hello.txt", "text/plain; charset=utf-8",request, handler)
    
def hi(request,handler):
    handler.request.sendall(b"HTTP/1.1 301 Moved Permanently\r\nContent-Length: 0\r\nLocation: /hello\r\n\r\n")
  

def four_oh_four(handler):
    handler.request.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: 36\r\n\r\nThe requested content does not exist")

def get_username(request):
    cookies = get_cookies(request)
    auth_token = cookies["auth_token"]
    hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()
    username = usersdb.userLookup(hashed_token)    
    return username

def get_cookies(request):
    Cookies = request.headers["Cookie"]
    cookie_dict = Cookies.split("; ")
    cookies = {}
    for cookie in cookie_dict:
        key = cookie.split("=")[0]
        val = cookie.split("=")[1]
        cookies[key] = val
    return cookies

def home(request, handler):
    html=""
    if "Cookie" in request.headers:
        cookies = get_cookies(request)
        if "auth_token" in cookies:
            username = get_username(request)
            #check if the user/ auth token pair exists
            if username != False:
                #once user is authenticated xsrf added to their collection
                xsrf = secrets.token_urlsafe(32)
                usersdb.addXSRF(xsrf,username)
                welcome = username 
                #checks if favorite professor is on file
                fav = usersdb. fav_prof_lookup(username)
                if fav != False:
                    fav_prof = ""
                    if fav == "I'm a psychopath":
                        fav_prof = "hello, I'm "+username +" and " + fav
                    else:
                        fav_prof = "Hi my fav UB CSE professor is "+fav
                    #hey = username+""s chat:" #could use for dms
                    html = render_template("public/index.html", {"welcome":welcome,
                                                            "xsrf":xsrf,
                                                            "username":username,
                                                            "fav_prof": fav_prof
                                                            # "images":handler.images
                                                            }).encode()

                #no favorite professor set
                else:
                    fav_prof = "I don't have a favorite UB CSE professor 😔"
                    #hey = username+""s chat:" #could use for dms
                    html = render_template("public/index.html", {"welcome":welcome,
                                                            "xsrf":xsrf,
                                                            "username":username,
                                                            "fav_prof": fav_prof
                                                            # "images":handler.images
                                                            }).encode()
                response = generate_response(html, "text/html; charset=utf-8", "200 OK")
                handler.request.sendall(response)
            else:
                login(request,handler)
        else:
            login(request,handler)
    else:       
        login(request,handler)

def registered(request, handler):
        send_file("public/register.html", "text/html; charset=utf-8", request, handler)

def registration(request, handler):
    body =request.body
    body_dict = json.loads(body)
    username = body_dict["username"]
    if usersdb.repeat_username_check(username):
        four_oh_four(handler)
    else:
        password = (body_dict["password"]).encode()
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password,salt)
        user_dict = {"username":username,"hash":hash,"salt":salt}
        usersdb.createAccount(user_dict)
        handler.request.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n")

def login(request, handler):
    send_file("public/login_page.html", "text/html; charset=utf-8", request, handler)

def newlogin(request, handler):
    body = request.body
    body_dict = json.loads(body)
    #get username and password
    if "fav_prof" in body_dict:
        add_prof(request,handler)
    else:
        username = body_dict["username"]
        password = (body_dict["password"]).encode()
        #gen salt and append to password                    
        salt = usersdb.retrieve_salt(username)
        hashed_login = bcrypt.hashpw(password,salt)
        hash_from_db = usersdb.retrieve_hash(username)
    
    # true if password matches
    if hashed_login == hash_from_db:
        #generate token
        token = secrets.token_urlsafe(32)                        
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        usersdb.add_auth(username,hashed_token)
        #send 200 response + token cookie + auth token
        handler.request.sendall(("HTTP/1.1 200 OK\r\nContent-Length: 0\r\nSet-Cookie: auth_token="+token+"; Max-Age=3600; HttpOnly\r\nLocation: /\r\n\r\n").encode())

    #else doesnt match
    else:
        four_oh_four(handler)

def add_prof(request:Request, handler):
    body = request.body
    body_dict = json.loads(body)
    username = body_dict["username"]
    fav = body_dict["fav_prof"]
    usersdb.add_fav(username,fav)
    handler.request.sendall(("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\nContent-Length: 0\r\n\r\n").encode())
