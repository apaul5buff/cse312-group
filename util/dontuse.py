'''

from urllib import response
from util.response import generate_response
from util.router import Route
import hashlib
import base64
import util.response
import random
import json
import util.wsbase as db
from util.response import chat_response

def add_paths(router):
    router.add_route(Route('GET', '/websocket', ws))
    router.add_route(Route('GET', '/chat-history', chat))

def chat(request,handler):
    posts=db.list_all()
    response=chat_response(json.dumps(posts).encode())
    handler.request.sendall(response)


def ws(request,handler):
    ws_key=request.headers["Sec-WebSocket-Key"]+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    result = base64.b64encode(hashlib.sha1(str.encode(ws_key)).digest())
    response=util.response.ws_response(result)
    handler.request.sendall(response) # send intial response to do websockets

    username= "user" + str(random.randint(0,1000))
    handler.ws_connections.append(handler)
    handler.ws_users[username]=handler # add user
    while True:
        ws_data=handler.request.recv(1024)
        if len(ws_data)==0:
            return
         #start connnection loop
        #parse ws frame headers up to opcode
        #opcode is 1000 remove from lists - break
        bits=[format(byte, '08b') for byte in ws_data]
        print(bits) #turn data into a list of bits
        opcode=bits[0][4:8]
        if(opcode=='1000'): #if code says to close connection
            #handler.ws_connections.append(handler)
            del handler.ws_users[username]
            break

        payloadLen=bits[1][1:8]
        masking=[]#this will be a list of the 4 masking bytes in bit form
        payload=[]# this will be a list of bytes in the frame after the mask bytes
        if(payloadLen=='1111110'):#16 bit
            payloadLen="".join(bits[2:4])
            masking=bits[4:8]
            payload=bits[8:]
        elif(payloadLen=="1111111"):#64bit
            payloadLen="".join(bits[2:10])
            masking=bits[10:14]
            payload=bits[14:]
        else:
            #next 4 bytes are masking key
            masking=bits[2:6]
            payload=bits[6:]
        payloadLen=int(payloadLen,2) #turn bits into and int
        print("payloadLen: "+str(payloadLen))
        count=0
        ret=[]
        #print(masking)
        #print(payload)
        while(count<payloadLen): # while we have not read payload len bits
            for currentPayload in payload: #for currently obtained payload
                maskIndex=(count % 4)
                currentMask=masking[maskIndex]
                unmaskedInt=int(currentMask,2)^int(currentPayload,2)
                xor="{0:b}".format(unmaskedInt)
                while(len(xor)<8):
                    xor="0"+xor
                ret.append(xor)
                count+=1
                if(count==payloadLen):
                    break
            if(count==payloadLen):
                break
            ws_data=handler.request.recv(1024)
            if len(ws_data)==0:
                return
            bits=[format(byte, '08b') for byte in ws_data]
        finalPayload="".join(ret)
        #print(finalPayload)
        #temp=finalPayload.to_bytes((finalPayload.bit_length() + 7) // 8, 'big').decode()
        temp=(int(finalPayload, 2).to_bytes((len(finalPayload) + 7) // 8, byteorder='big')).decode()
        body_dict=json.loads(temp)
        #print(temp)

        #frame has been read now to reply

        unsafeMessage=body_dict["comment"]      
        safeMessage=escape_html(unsafeMessage)
        del body_dict["comment"]
        body_dict["username"]=username
        body_dict["comment"]=safeMessage
        returnMessage=json.dumps(body_dict)
        del body_dict['messageType']
        db.create(body_dict)
        messageByte=returnMessage.encode()
        #add message to dict and encode
        binaryMessage=''.join(format(byte, '08b') for byte in messageByte)
        length=len(binaryMessage)//8
        if(length<126):
            #7 bit length
            size=bin(length).lstrip('0b')
            while(len(size)<7):
                size="0"+size
            lenByte=("0"+size)
        elif(length<65536):
            #first 7 bits 1111110
            lenByte="01111110"
            size=bin(length).lstrip('0b')
            while(len(size)<16):
                size="0"+size
            lenByte+=size
            #16 bit length
        else:
            #first 7 bits 1111111
            lenByte="01111111"
            size=bin(length).lstrip('0b')
            while(len(size)<64):
                size="0"+size
            lenByte+=size
            #64 bit length
        returnFrame="10000001"+lenByte+binaryMessage
        print("poop")
        print(returnFrame)
        idk=int(returnFrame, 2).to_bytes((len(returnFrame) + 7) // 8, byteorder='big')
        handler.ws_users[username]
        for hand in handler.ws_users:
            value=handler.ws_users[hand]
            value.request.sendall(idk)

        #mod 4 and then minus 1 to get index for masking
        #have counter for length and mod
        #parse payload length
        # buffer if need

        #process ws frame
        #send frames as needed
        #send frame first byte 10000001
        #mask is 0 reverse the length stuff then payload
        #broadcast to all connects if chat message
        #send to connection if webrtc
    #send disconnect?

def ws_upgrade(request,handler):
    headers=request.headers
    if(headers["Connection"]=="Upgrade"):
        if(headers["Upgrade"]=="websocket"):
            if "Sec-WebSocket-Key" in headers:
                return True

def escape_html(input):
    return input.replace('&',"&amp;").replace('<',"&lt;").replace('>',"&gt;")

'''