from urllib import request
import util.database as db
from util.request import Request

def render_templete(images_list): 
    print(images_list)
    html_data = read_file("public/index.html")
    # print(html_data)
    messages_data = db.messages_collection.find()
    messages_html = ""
    
    for message in messages_data:
        # user: comment
        # message["kjeyname"]
        messages_html += "<p>" + message["id"] + ":" + message["comment"] + "</p>\n"
    
    html_data = html_data.replace("{{comments}}", messages_html)
    image_str = ""
    if len(images_list) > 0:
        for name in images_list:
            image_str += ("<img id=\"uimage\" src=\"%s\">" % name)
        html_data = html_data.replace("{{images}}", image_str)
    else:
        html_data = html_data.replace("{{images}}", "")
    return html_data

def read_file(file_name):
    with open(file_name, "r") as html_file:
        file_bytes = html_file.read()
    return file_bytes
