class Request:
    new_line=b'\r\n'
    blank_line=b'\r\n\r\n'
    
    def __init__(self,request:bytes):
        [request_line,header_bytes,self.body]=split_request(request)
        [self.method,self.path,self.httpV]=parse_request(request_line)
        self.headers=parse_headers(header_bytes)
        self.top=len(request_line)+len(header_bytes)

def split_request(request:bytes):
    first=request.find(Request.new_line)
    blank_spot=request.find(Request.blank_line)
    request_line=request[:first]
    header_bytes=request[(first+len(Request.new_line)):blank_spot]
    body=request[(blank_spot+len(Request.blank_line)):]
    return[request_line,header_bytes,body]

def parse_request(request_line: bytes):
    return request_line.decode().split(' ')

def parse_headers(headers_raw:bytes):
    headers={}
    lines_str=headers_raw.decode().split(Request.new_line.decode())
    for line in lines_str:
        splits=line.split(":")
        headers[splits[0].strip()]=splits[1].strip()
    return headers

def parse_multipart(request: Request):
    request.parts ={}
    ct = request.headers.get("Content-Type")
    key = "boundary="
    raw_boundary= ct[ct.find(key) + len(key):].strip()
    first= ("--" + raw_boundary + "\r\n").encode()
    mid=("\r\n--" + raw_boundary + "\r\n").encode()
    last=("\r\n--" + raw_boundary + "--").encode()
    processing_body=request.body
    first_index=processing_body.find(first)
    if first_index!=0:
        print("something messed up")

    processing_body=processing_body[len(first):]
    len_before= len(processing_body)
    processing_body= processing_body[:processing_body.find(last)]
    len_after=len(processing_body)
    if len_before -len_after != len(last):
        #print(processing_body)
        print("what is happening!?")
    
    raw_parts=processing_body.split(mid)

    for part in raw_parts:
        new_part= b"fake request line\r\n" +part
        req= Request(new_part)
        name = req.headers.get("Content-Disposition").split(";")[1].split("=")[1].replace('"',"")
        request.parts[name]= req.body


    