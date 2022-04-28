from urllib import response
import util.wsbase as db

import socketserver
import hashlib
import base64
import random
import json

from server import myTCPhandler
from util.request import Request
from util.router import Route
from util.response import forbid, redirect
from util.request import parse_multipart
from util.response import generate_response,ws_response,chat_response

def add_paths(router):
    router.add_route(Route('GET', '/websocket', websocket_request))
    router.add_route(Route('GET', '/chat-history', chat))
    router.add_route(Route('GET','/active-users',users))

def users(request,handler):
    connections=myTCPhandler.ws_connections
    userList = [ user['username'] for user in connections ]
    response=generate_response(json.dumps(userList).encode())
    handler.request.sendall(response)

def chat(request,handler):
    posts=db.list_all()
    response=chat_response(json.dumps(posts).encode())
    handler.request.sendall(response)

def compute_accept(key):
    guid="258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    to_hash=(key+guid).encode()
    hash_btyes=hashlib.sha1(to_hash).digest()
    encoded_hash= base64.b64encode(hash_btyes)
    return encoded_hash

def websocket_request(request:Request,handler:socketserver.BaseRequestHandler):
    response=ws_response(compute_accept(request.headers["Sec-WebSocket-Key"]))
    handler.request.sendall(response)

    username= "user" + str(random.randint(0,1000))
    myTCPhandler.ws_connections.append({'username':username,'socket':handler})
    while True:
        ws_data=handler.request.recv(1024)
        if len(ws_data)==0:
            return
        ws_frame=WSframe(ws_data)
        if ws_frame.opcode==8:
            to_delete=None
            for connection in myTCPhandler.ws_connections:
                if connection['socket']==handler:
                    to_delete=connection
            if to_delete:
                myTCPhandler.ws_connections.remove(to_delete)
            break
        while not ws_frame.finished_buffering:
            more_bytes=handler.request.recv(1024)
            ws_frame.frame_bytes=ws_frame.frame_bytes+more_bytes
            ws_frame.checkPayload()
        ws_frame.extractPayload()
        message_json=ws_frame.payload.decode()
        body_dict=json.loads(message_json)
        message_type=body_dict['messageType']

        if message_type=='chatMessage':
            unsafeMessage=body_dict["comment"] 
            safeMessage=escape_html(unsafeMessage)
            del body_dict["comment"]
            body_dict["username"]=username
            body_dict["comment"]=safeMessage
            returnMessage=json.dumps(body_dict).encode()
            del body_dict['messageType']
            db.create(body_dict)
            #weird
            to_send=generate_frame(returnMessage)
            for user in myTCPhandler.ws_connections:
                user['socket'].request.sendall(to_send)

        elif message_type=='webRTC-answer':
            other_handler=get_other_handler(handler)
            to_send={'messageType':'webRTC-answer', 'answer':body_dict['answer']}
            mess=json.dumps(to_send).encode()
            frame=generate_frame(mess)
            other_handler.request.sendall(frame)
        elif message_type=='webRTC-offer':
            other_handler=get_other_handler(handler)
            to_send={'messageType':'webRTC-offer', 'offer':body_dict['offer']}
            mess=json.dumps(to_send).encode()
            frame=generate_frame(mess)
            other_handler.request.sendall(frame)
        elif message_type=='webRTC-candidate':
            other_handler=get_other_handler(handler)
            to_send={'messageType': 'webRTC-candidate', 'candidate': body_dict['candidate']}
            mess=json.dumps(to_send).encode()
            frame=generate_frame(mess)
            #error in Web RTC stuff somewhere
            other_handler.request.sendall(frame)
        elif message_type=="dmMessage":
            unsafeMessage=body_dict["comment"] 
            safeMessage=escape_html(unsafeMessage)
            unsafeName=body_dict["toUser"] 
            safeName=escape_html(unsafeName)
            del body_dict["comment"]
            del body_dict["toUser"]
            body_dict["username"]=username
            body_dict["comment"]=safeMessage
            returnMessage=json.dumps(body_dict).encode()
            to_send=generate_frame(returnMessage)
            for connection in myTCPhandler.ws_connections:
                if connection['username']==safeName:
                    to_user=connection['socket']
                    to_user.request.sendall(to_send)

        else:
            print("error invalid message type")

def get_other_handler(handler): 
    #this is  not the error
    for connection in myTCPhandler.ws_connections:
        if connection['socket'] != handler:
            return connection['socket']
    print("error only 1 connection")
    return None

def generate_frame(payload_bytes):
    #might be an error here
    #PRETTY SURE ERROR HERE
    #MAYBE NOT GETTING ENOUGH DATA? idk
    payloadLength=len(payload_bytes)
    frame=b'\x81'
    if payloadLength<126:
        frame= frame+payloadLength.to_bytes(1,'big')
    elif payloadLength<65536:
        frame= frame+b'\x7e'+payloadLength.to_bytes(2,'big')
    else:
        frame= frame+b'\x7f'+payloadLength.to_bytes(8,'big')
    frame= frame+payload_bytes
    return frame
    
class WSframe:
    def __init__(self, frame_bytes):
        self.frame_bytes=frame_bytes
        self.fin=1
        self.opcode=0
        self.maskbit=0

        self.payloadLength=27
        self.payload=b'123456789012345678901234567'
        self.firstMask_or_payloadByte=0
        self.parseheaders()
        self.parse_payloadLength()
        self.finished_buffering=False
        self.checkPayload()

    def checkPayload(self):
        offset=self.firstMask_or_payloadByte
        if self.maskbit==1:
            offset=offset+4
        rawPayload=self.frame_bytes[offset:]
        if len(rawPayload)< self.payloadLength:
            return
        else:
            self.finished_buffering=True
    
    def extractPayload(self):
        self.checkPayload()
        firstByte=self.firstMask_or_payloadByte
        if self.maskbit == 1:
            mask=self.frame_bytes[firstByte:firstByte+4]
            payload=b''
            for i in range(firstByte+4,firstByte+4+self.payloadLength):
                mask_byte_index=(i-firstByte)%4
                payload=payload+(self.frame_bytes[i]^mask[mask_byte_index]).to_bytes(1,'little')
            self.payload=payload
        else:
            self.payload=self.frame_bytes[firstByte:firstByte+self.payloadLength]
    
    def parseheaders(self):
        self.opcode=self.frame_bytes[0]&31
        self.fin=self.frame_bytes[0]>>7
        self.maskbit=self.frame_bytes[1]>>7
    
    def parse_payloadLength(self):
        first=self.frame_bytes[1]&127
        if first<126:
            self.payloadLength=first
            self.firstMask_or_payloadByte=2
        elif first==126:
            payloadLength=int(self.frame_bytes[2])
            payloadLength=payloadLength<<8
            payloadLength=payloadLength+self.frame_bytes[3]
            self.payloadLength=payloadLength
            self.firstMask_or_payloadByte=4
        elif first==127:
            payloadLength=int(self.frame_bytes[2])       
            for i in range(3,10):
                payloadLength=payloadLength<<8
                payloadLength=payloadLength+self.frame_bytes[i]
            self.payloadLength=payloadLength
            self.firstMask_or_payloadByte=10
        else:
            print(" parse error")
            
def ws_upgrade(request,handler):
    headers=request.headers
    if(headers["Connection"]=="Upgrade"):
        if(headers["Upgrade"]=="websocket"):
            if "Sec-WebSocket-Key" in headers:
                return True

def escape_html(input):
    return input.replace('&',"&amp;").replace('<',"&lt;").replace('>',"&gt;")