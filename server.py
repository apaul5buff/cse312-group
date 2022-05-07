from http import client
import socketserver
import sys
import ssl

from util.request import Request
from util.router import Router
from util.from_paths import add_paths as form_paths
from util.user_paths import add_paths
from util.static_paths import add_paths as other_paths
import util.websockets 

class myTCPhandler(socketserver.BaseRequestHandler):
    #clients=[]
    images = []
    
    def __init__(self, request, client_address, server):
        self.router= Router()
        add_paths(self.router)
        other_paths(self.router)
        form_paths(self.router)
        util.websockets.add_paths(self.router)
        super().__init__(request, client_address, server)

    ws_connections=[]
    counter = 0    

    def handle(self):
        received_data=self.request.recv(1024)
        if len(received_data)==0:
            return
        #read http headers
        #buffer if needef
        print(received_data.decode())
        print("\n\n")
        sys.stdout.flush()
        sys.stderr.flush()
        request= Request(received_data)
        #if ws request
        if(util.websockets.ws_upgrade(request,self)):
            self.router.handle_request(request,self)
        else:
            data=received_data
            bod=request.body
            if(request.method=="POST"):
                while(len(bod)<int(request.headers["Content-Length"])):
                    data+=self.request.recv(1024)
                    request= Request(data)
                    bod=request.body
            request= Request(data)

            print("\n\n")
            sys.stdout.flush()
            sys.stderr.flush()
            self.router.handle_request(request, self)
            sys.stdout.flush()
            sys.stderr.flush()

        #self.request.sendall("HTTP/1.1 200 OK\r\nContent-Length: 5\r\nContent-Type: text/plain; charset=utf-8\r\n\r\nhello".encode())


if __name__ == "__main__":
    host="0.0.0.0"
    port=8000
    secure = False
    
    server=socketserver.ThreadingTCPServer((host,port), myTCPhandler)

    print("Listening on port " + str(port))
    sys.stdout.flush()
    sys.stderr.flush()
    if not secure:
        server.serve_forever()
    else: 
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain('cert.pem', 'private.key')
        socket=server.socket
        with ctx.wrap_socket(socket, server_side=True) as secure_socket:
            server.sokcet = secure_socket
            server.serve_forever()