
def generate_response(body: bytes, content_type:str = 'text/plain; charset=utf-8', response_code: str = '200 OK'):
    response = b'HTTP/1.1 ' +response_code.encode()
    response += b'\r\nContent-Length: ' +str(len(body)).encode()
    response +=b'\r\nContent-Type: ' +content_type.encode()
    response +=b'\r\nX-Content-Type-Options: nosniff'
    response += b'\r\n\r\n'
    response += body
    return response 

def redirect(path:str):
    response=b'HTTP/1.1 302 Redirect'
    response+= b'\r\nContent-Length: 0'
    response+= b'\r\nLocation: '+path.encode()
    response+= b'\r\n\r\n'
    return response

def forbid(path:str):
    response=b'HTTP/1.1 403 Forbidden'
    response+= b'\r\nContent-Length: 0'
    response+= b'\r\nLocation: '+path.encode()
    response+= b'\r\n\r\n'
    return response
    
def ws_response(key:str):
    response=b'HTTP/1.1 101 Switching Protocols'
    response+= b'\r\nConnection: Upgrade'
    response+= b'\r\nUpgrade: websocket'
    response+= b'\r\nSec-WebSocket-Accept: '+key
    response+= b'\r\n\r\n'
    return response

def chat_response(body: bytes, content_type:str = 'application/json; charset=utf-8', response_code: str = '200 OK'):
    response = b'HTTP/1.1 ' +response_code.encode()
    response += b'\r\nContent-Length: ' +str(len(body)).encode()
    response +=b'\r\nContent-Type: ' +content_type.encode()
    response +=b'\r\nX-Content-Type-Options: nosniff'
    response += b'\r\n\r\n'
    response += body
    return response 