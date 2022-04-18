def render_templete(html_filename, data):

    with open(html_filename) as html_file:
        template= html_file.read()
        template= replace_placeholders(template,data)
        template= render_loop(template,data)
        template=render_loop_img(template,data)
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