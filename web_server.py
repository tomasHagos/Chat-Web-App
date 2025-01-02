import threading 
import socket
import json 
import re
import os
import os.path
import sys



def http_request_parse(http_request):
    #split the http_request on /n
    http_request = http_request.splitlines()
    if(len(http_request) > 0):
        request_line = http_request[0].split(" ")
        #check if the request line is complete.
        if(len(request_line) >=3):
            method,path,http_type = request_line[0],request_line[1],request_line[2]
            headers = {}
            index = 1
            for i in range(1,len(http_request)):
                # if we read this we are reading the body
                if(http_request[i]==""):
                    break
                header_line = http_request[i].split(":")
                headers[header_line[0]] = header_line[1]
                index += 1

            body = ''
            if(index+1 < len(http_request)):
                body += http_request[index+1]

            return {
                'method':method,
                'path':path,
                'http_type':http_type,
                'headers':headers,
                'body':body

            }
    return {}

#/
def serve_index_page(request:dict):
    with open('index.html','r') as html_file:
        content = html_file.read()
    http_response= """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length:{} \r\n\r\n"""
    sending_content=content.encode()
    response = http_response.format(len(sending_content))
    response += content
    return response.encode()

#/favicon
def serve_favicon():
    with open('favicon.ico','rb') as image:
        favicon_data = image.read()
    http_response = """HTTP/1.1 200 OK\r\nContent-Type:image/x-icon\r\nContent-Lenght:{}\r\n\r\n"""
    http_response = http_response.format(len(favicon_data))
    http_response = http_response.encode()
    http_response += favicon_data
    return http_response


def bad_request_string():
    bad_request_string = "HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nContent-Length:{}\r\n\r\n"
    return bad_request_string

def bad_request(message):
      http_response = bad_request_string()
      response = {'error':'Bad request 400','message':message}
      response_json = json.dumps(response)
      http_response = http_response.format(len(response_json.encode()))
      http_response += response_json
      return http_response.encode()

def empty_user_name_response():
    http_response = bad_request_string()
    response = {'error':'bad request', 'message':'Please enter a valid username!'}
    response_json = json.dumps(response)
    http_response = http_response.format(len(response_json.encode()))
    http_response += response_json
    return http_response.encode()

#GET /api/login
def get_login(request:dict):
    http_response = """HTTP/1.1 200 OK\r\nContent-Type:application/json\r\nContent-Lenght:{}\r\n\r\n"""
    header = request.get("headers","NONE")
    body = {'status':"logged out"}

    if(header!= "NONE"):
        cookie = header.get("Cookie","NONE")
        if(cookie != "NONE"):
            body = {'status':'logged in','username':cookie}
           
    
    json_body = json.dumps(body)
    http_response = http_response.format(len(json_body.encode()))
    http_response += json_body
    return http_response.encode()
    
#POST /api/login
def post_login(request:dict):
    http_response = """HTTP/1.1 200 OK\r\nContent-Type:application/json\r\nContent-Lenght:{}\r\n"""
    body = request.get("body","NONE")
    
    #body is in every request(html parser function does) but if its empty then the request doesn't have a body
    if(body):
        login_data = json.loads(body)
        username = login_data.get("username","NONE")
        if(username):
            response_body = {'message':f'Welcome {username}!'}
            json_body = json.dumps(response_body)
            sending_body = json_body.encode()
            http_response = http_response.format(len(sending_body))
            http_response += f"Set-Cookie:username={username}; HttpOnly; Path=/\r\n\r\n"
            http_response += json_body
            return http_response.encode()
        #adding this case for users that are not using the client file I provided.
        return empty_user_name_response()
    
    return bad_request("No body provided")
    

def get_request_chatServer(number:int,chat_HOST,chat_PORT):
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as chat_socket:
           chat_socket.connect((chat_HOST,chat_PORT))
           data = {'method':'GET', 'id':number}
           data_json = json.dumps(data)
           chat_socket.sendall(data_json.encode())
           data = chat_socket.recv(6144)
            
           http_response = """HTTP/1.1 200 OK\r\nContent-Type:application/json\r\nContent-Lenght:{}\r\n\r\n"""

           http_response = http_response.format(len(data))
           data_string = data.decode('utf-8')
           http_response += data_string
           data_object = json.loads(data_string)

           return http_response.encode()

def not_found():
    http_response = "HTTP/1.1 404 Not Found\r\nContent-Type:application/json\r\nContent-Length:{}\r\n\r\n"
    body = {"error":"Not Found 404","message":"The requested resource could not be found."}
    json_body = json.dumps(body)
    http_response = http_response.format(len(json_body.encode()))
    http_response += json_body
    return http_response.encode()

def unauthorized():
    unauthorized_string = "HTTP/1.1 401 Unauthorized\r\nContent-Type: application/json\r\nContent-Length:{}\r\n\r\n"
    body = {"error":"Unauthorized 401","message":"Not logged In"}
    body_json = json.dumps(body)
    unauthorized_http= unauthorized_string.format(len(body_json.encode()))
    unauthorized_http += body_json
    return unauthorized_http.encode()

def method_not_implemented():
    http_response = "HTTP/1.1 405 Method Not Implemented\r\n Content-Type:application/json\r\nContent-Length:{}\r\n\r\n"
    body = {"error":"Method not Implemented 405","message":"The requested method is not supported"}
    json_body = json.dumps(body)
    http_response = http_response.format(len(json_body.encode()))
    http_response += json_body
    return http_response.encode()

        
def get_username_from_cookie(request):
    headers = request.get("headers","NONE")
    if(headers != "NONE"):
        cookie = headers.get("Cookie","NONE")
        if(cookie != "NONE"):
            cookie_list = cookie.split(";")
            for word in cookie_list:
                word_list = word.split("=")
                if(len(word_list) == 2):
                    if(word_list[0].lstrip()=="username"):
                        return word_list[1]
    return ""

def has_cookie(request:dict):
    headers = request.get("headers","NONE") 
    if(headers != "NONE"):
        cookie = headers.get("Cookie","NONE")
        if(cookie != "NONE"):
            username = get_username_from_cookie(request)
            if username:
                return True
    return False
           
def serve_messages(request:dict, chat_HOST, chat_PORT):

    if(has_cookie(request)):
        path = request.get("path","NONE")
        path_parts = path.split("?",1)
        #we have a query string
        if(len(path_parts) > 1):
            query_string = path_parts[1]
            queries= query_string.split("&")
            for query in queries:
                key_value = query.split("=",1)
                if(len(key_value) == 2):
                    key,value = key_value[0].lower(), key_value[1]
                    if(key == "last") and value:
                        try:
                            id = int(value)
                            return get_request_chatServer(id,chat_HOST, chat_PORT)
                        except ValueError:
                            return bad_request("Invalid value for query string")
        
        #if it has no query strings just get all the messages that have been sent.
        return get_request_chatServer(0,chat_HOST,chat_PORT)
    
    
    return unauthorized()


#post /api/messages endpoint
def post_messages(request:dict,chat_HOST, chat_PORT):
    if(has_cookie(request)):
        body = request.get("body","NONE")
        if(body != "NONE"):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as chat_socket:
                chat_socket.connect((chat_HOST,chat_PORT))
                data_sent = {'method':'POST','message':body}
                data_sent = json.dumps(data_sent)
                chat_socket.sendall(data_sent.encode())

                return "HTTP/1.1 200 OK\r\n\r\n".encode()
               
        return bad_request("No body in the request")
    
    return unauthorized()

#DELETE /api/login
def log_out(request:dict):
    if(has_cookie(request)):
        http_response = "HTTP/1.1 200 OK\r\nSet-Cookie: username='';expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; HttpOnly\r\nContent-Type: application/json\r\nContent-Length:{}\r\n\r\n"
        body = {"message":"You are now logged out."}
        json_body = json.dumps(body)
        http_response = http_response.format(len(json_body.encode()))
        http_response += json_body
        return http_response.encode()
    return unauthorized()


def find_file_path(filename):
    for dirpath,dirns,files in os.walk('.'):
        if filename in files:
            #if a target file is found return the full path to it.
            return os.path.join(dirpath,filename)
    
    return ""


def find_content_type(filename:str):
    if(filename.endswith(".html")):
        return "text/html"
    if(filename.endswith(".js")):
        return "application/javascript"
    if(filename.endswith(".jpeg")):
        return "image/jpeg"
    if(filename.endswith(".png")):
        return "image/png"
    if(filename.endswith(".py")):
        return "application/python"
    if(filename.endswith(".txt")):
        return "text/plain"
    return ""
    
def file_system(request:dict):
    if(has_cookie(request)):
        path = request.get("path","NONE")
        if(path != "NONE"):
            #extract the file
            filename = os.path.basename(path)
            #find the full file path
            file_path = find_file_path(filename)
            #if the file is found
            if file_path:
                http_response = 'HTTP/1.1 200 OK\r\n'
                content_type = find_content_type(filename)
                if content_type:
                    http_response += "Content-Type: "+content_type+"\r\n"
                    with open(file_path,'rb') as fileB:
                        fileContents = fileB.read()
                        http_response += "Content-Length: "+str(len(fileContents))+"\r\n\r\n"
                        http_response = http_response.encode()
                        http_response += fileContents
                        return http_response
                return not_found()

            return not_found()
    else:
        return unauthorized()


def delete_messages(request:dict,chat_HOST,chat_PORT):
    if(has_cookie(request)):
        path = request.get("path","NONE")
        if(path != "NONE"):
            path_list = path.split('/')
            print(path_list)
            if(len(path_list) == 4):
                username = path_list[3]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as chat_socket:
                    chat_socket.connect((chat_HOST,chat_PORT))
                    data = {'method':'DELETE', 'id':username}
                    data_sent = json.dumps(data)
                    chat_socket.sendall(data_sent.encode())
                    return "HTTP/1.1 200 OK\r\n\r\n".encode()
            return bad_request("Bad Path format")
        return bad_request("no path found")
    return unauthorized()

def get_handler(request:dict, chat_HOST, chat_PORT):
    path = request.get("path","NONE")
    if(path == "NONE"):
        return bad_request("Bad HTTP format. No path found.")
    if(path == "/"):
        return serve_index_page(request)
    if(path == "/favicon.ico"):
        return serve_favicon()
    if(path == "/api/login"):
        return get_login(request)
    pattern = r'/api/messages\?.*'
    if(path == '/api/messages' or re.match(pattern,path)):
        return serve_messages(request, chat_HOST, chat_PORT)
    
    return file_system(request)
   

def post_handler(request:dict,chat_HOST,chat_PORT):
    path = request.get("path","NONE")
    if(path == "NONE"):
        return bad_request("Bad HTTP format. No path found.")
    if(path == "/api/login"):
        return post_login(request)
    if(path=='/api/messages'):
        return post_messages(request,chat_HOST,chat_PORT)
    return not_found()

def delete_handler(request:dict,chat_HOST,chat_PORT):
    path = request.get("path","NONE")
    if(path == "NONE"):
       return bad_request("Bad HTTP format. No path found.")
    if(path == "/api/login"):
        return log_out(request)
    pattern = r'/api/messages/.*'
    if(re.match(pattern,path)):
        return delete_messages(request, chat_HOST, chat_PORT)
    return not_found()
        
def process_request(request:dict,chat_HOST,chat_PORT):
    method = request.get("method","NONE")
    if(method == "NONE"):
        return bad_request("Invalid HTTP FORMAT")
    if(method.lower() == "get"):
        return get_handler(request,chat_HOST,chat_PORT)
    if(method.lower()=="post"):
        return post_handler(request,chat_HOST,chat_PORT)
    if(method.lower()=="delete"):
        return delete_handler(request, chat_HOST,chat_PORT)
    
    return method_not_implemented()

def retrieve_request_respond(conn,chat_HOST, chat_PORT):
    data = conn.recv(6144)
    if data:
        data = data.decode('utf-8')
        print(data)
        request = http_request_parse(data)
        response = process_request(request,chat_HOST, chat_PORT)
        conn.sendall(response)
    conn.close()

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    if(len(sys.argv) >=2):
        HOST=''
        PORT = 8307
        chat_HOST = sys.argv[1]
        chat_PORT = 8306
        s.bind((HOST,PORT))
        s.listen()
        print(f"Web server listening on port {PORT}")
        while True:
            conn, addr = s.accept()
            print(f"New connection by {addr}")
            thread_process = threading.Thread(target=retrieve_request_respond,args=(conn,chat_HOST,chat_PORT,))
            thread_process.start()
    else:
        print("Please Enter the where the chat server is being hosted!")
