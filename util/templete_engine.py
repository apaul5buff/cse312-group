from urllib import request
import util.database as db
from util.request import Request

def render_image(images_list): 
    print(images_list)
    html_data = read_file("public/images.html")
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
            image_str += ("<img id=\"uimage\" src=\"%s\">" % name) + "<br>"
        html_data = html_data.replace("{{images}}", image_str)
    else:
        html_data = html_data.replace("{{images}}", "")
    return html_data

def read_file(file_name):
    with open(file_name, "r") as html_file:
        file_bytes = html_file.read()
    return file_bytes

def render_template(html_filename, data):

    with open(html_filename) as html_file:
        template= html_file.read()
        template= replace_placeholders(template,data)
        # template = render_images()
        # template= render_loop(template,data)
        # template=render_loop_img(template,data)
        return template
    
def replace_placeholders(template,data):
    replaced_template=template
    for  placeholder in data.keys():
        if isinstance(data[placeholder], str):
            replaced_template= replaced_template.replace("{{"+placeholder+"}}",data[placeholder])
    return replaced_template

def render_loop(template,data):
    if "loop_data" in data:
        loop_start_tag= "{{loop}}"
        loop_end_tag="{{end_loop}}"

        start_index=template.find(loop_start_tag)
        end_index=template.find(loop_end_tag)
        
        loop_template=template[start_index+len(loop_start_tag):end_index]
        loop_data=data["loop_data"]

        loop_content= ""
        for single in loop_data:
            loop_content += replace_placeholders(loop_template,single)

        final=template[:start_index]+loop_content+template[end_index+len(loop_end_tag):]
        return final

def render_loop_img(template,data):
    if "loop_img" in data:
        loop_start_tag= "{{loop_img}}"
        loop_end_tag="{{end_loop_img}}"

        start_index=template.find(loop_start_tag)
        end_index=template.find(loop_end_tag)
        
        loop_template=template[start_index+len(loop_start_tag):end_index]
        loop_data=data["loop_img"]

        loop_content= ""
        for single in loop_data:
            loop_content += replace_placeholders(loop_template,single)

        final=template[:start_index]+loop_content+template[end_index+len(loop_end_tag):]
        return final