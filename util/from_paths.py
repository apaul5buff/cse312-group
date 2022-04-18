
from util.router import Route
from util.response import forbid, redirect
from util.request import parse_multipart
import util.chatdata as db
from PIL import Image
import io


chat_history=[] #make this database

def add_paths(router):
    router.add_route(Route('POST', "/image-upload", upload))
    router.add_route(Route('POST', "/insecure-chat", insecure_chat))

def upload(request,handler):
    parse_multipart(request)
    comment=escape_html(request.parts["comment"].decode())
    image=request.parts["upload"]
    token=request.parts["xsrf_token"].decode()
    check=db.check_token(token)
    if(check==None):
        response=forbid("/")
        handler.request.sendall(response)
    imageID= db.get_next_id()
    name="image{}.jpg".format(imageID)
    print(name)
    test= Image.open(io.BytesIO(image))
    test.save("image/"+name)
    
    image_dict={"comment":comment,"upload":name,"id":imageID}
    db.create(image_dict)

    response=redirect("/")
    handler.request.sendall(response)

def insecure_chat(request,handler):
    parse_multipart(request)
    username=escape_html(request.parts["username"].decode())
    message=escape_html(request.parts["message"].decode())
    #chat_history.append({"username":username,"message":message})
    db.create_post({"username":username,"message":message})
    response=redirect("/")
    handler.request.sendall(response)

def escape_html(input):
    return input.replace('&',"&amp;").replace('<',"&lt;").replace('>',"&gt;")
