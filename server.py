import socket
import time
from chat import Chat,ChatCollection #my own classes defined in another py file
import sys
import select
import re
import json 


def follow_protocol(client):
    s = "Please follow the protocol(Username: message)\n"
    client.sendall(s.encode())

def clean_up(terminal_clients):
    for c in terminal_clients:
        c.close()

def write_chat_to_clients(terminal_clients,data):
    data= data.encode()
    for c in terminal_clients:
        c.sendall(data)
         
def send_prev_messages(conn,chats:ChatCollection):
    messages= chats.get_all_messages(0)
    data = ''
    for i in range(0,len(messages)):
        curr_chat: Chat = messages[i]
        curr_message = curr_chat.get_message()
        if(len(curr_message) > 0):
            curr_message = curr_message.strip()
            data += curr_chat.get_username()+":"+curr_message+'\n'

    if(len(data)>0):
        conn.sendall(data.encode())       

def handle_get_requests(id:int,chats:ChatCollection,client):
    messages = []
    all_messages = chats.get_all_messages(id)
    for m in all_messages:
        curr_message= {'username':m.get_username(),'message':m.get_message(),'id':m.get_id()}
        messages.append(curr_message)
    
    messages_json = json.dumps(messages)
    client.sendall(messages_json.encode())

def write_web_message_to_tclients(terminal_clients,message):
    formatted_message = message.encode()
    for c in terminal_clients:
        c.sendall(formatted_message)

def write_web_message_to_DB(database,message):
    database.write(message+'\n')

def handle_post_requests(message,chats:ChatCollection):
    chats.add_web_message(message,time.time())

def format_username(username):
    return username.replace("%20"," ")

def handle_delete_request(username, chats:ChatCollection,database):
    chats.delete_messages(format_username(username))
    messages = chats.get_all_messages(0)
    database.seek(0) # go to the top 
    database.truncate(0) #clear it

    for i in range(0,len(messages)):
        username = messages[i].get_username()
        message = messages[i].get_message()
        database.write(username+":"+message+'\n')
  




def handle_web_client(client,chats:ChatCollection,data,terminal_clients,database):
    data_string = data.decode('utf-8')
    print("Recieved from a web client")
    print(data_string)
    data_json = json.loads(data_string)
    method = data_json.get('method','NONE')
    if(method != 'NONE'):
        if(method == 'GET'):
            id = data_json.get('id','NONE')
            if(id== 'NONE'):
                handle_get_requests(0,chats,client)
            else:
                handle_get_requests(id,chats,client)
        if(method == 'POST'):
            message = data_json.get('message','NONE')
            if(message != 'NONE'):
                message = json.loads(message)
                user_name= message.get("username","NONE")
                current_message = message.get("message","NONE")
                if(user_name != "NONE" and current_message != "NONE"):
                    formatted_message = user_name+":"+current_message
                    handle_post_requests(message,chats)
                    write_web_message_to_tclients(terminal_clients,formatted_message)
                    write_web_message_to_DB(database,formatted_message)
        
        if(method == 'DELETE'):
            username = data_json.get('id','NONE')
            if(username != "NONE"):
                handle_delete_request(username,chats,database)

        
      


def select_part(server_socket,web_socket,data_base,chats:ChatCollection):
    terminal_clients = []
    web_clients = []
    while True:
        
        try:
            inputs =  [server_socket,web_socket]+terminal_clients+web_clients
            readable,writable,exceptional = select.select(inputs,[],terminal_clients)


            #think about the web client's here...?
            for client in exceptional:
                terminal_clients.remove(client)
                client.close()
            
            for client in readable:
                #ready to accept new connection
                if client is server_socket:
                    conn, addr = server_socket.accept()
                    print('New connection by',addr)
                    terminal_clients.append(conn)
                    send_prev_messages(conn,chats)
                if client is web_socket:
                    conn, addr = web_socket.accept()
                    web_clients.append(conn)
                if client in terminal_clients:
                    try:
                        data= client.recv(6144)
                        if not data:
                            terminal_clients.remove(client)
                            client.close()
                        else:
                            data = data.decode('utf-8')
                            #using regular expressions
                            m = re.search('(:)(.*)',data)
                            if m:
                                if(m.group(2).lower().strip() == 'quit'):
                                    terminal_clients.remove(client)
                                    client.close()
                                else:
                                    #write to all terminal_clients here
                                    write_chat_to_clients(terminal_clients,data)
                                    chats.add_client_message(data,time.time())
                                    data_base.write(data+'\n')
                            else:
                                follow_protocol(client)
                    except OSError as e: 
                        #handle the case where recieve fails due to connection reset by peer
                        terminal_clients.remove(client)
                        client.close()
                if client in web_clients:
                    data=client.recv(6144)
                    if not data:
                        web_clients.remove(client)
                        client.close()
                    else:
                        handle_web_client(client,chats,data,terminal_clients,data_base)
                        try:
                            closing_data = b''
                            client.sendall(closing_data)
                        except OSError:
                            pass


            
        
        except KeyboardInterrupt as e:
            clean_up(terminal_clients)
            sys.exit(0)
        except Exception as e:
            print(f"Something has happened!: {e}")
            clean_up(terminal_clients)
            sys.exit(0)

def main():
        
        if(len(sys.argv) >=2):

            HOST = '' #for testing purposes
            PORT = 8305
            WEB_PORT = 8306

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:

                server_socket.bind((HOST,PORT))
                web_socket.bind((HOST,WEB_PORT))

                #adding options to the socket, we are saying that you can reuse the port while in timewait state. the 1 is saying allow it.
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                web_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                #here we are turing of the blocks for recv and accept. So if a client disconnects abrubtly we wouldn't keep on waiting. 
                #so recv() won't block. It will raise an exception if there is no data to be read immediately. 
                server_socket.settimeout(0)
                web_socket.settimeout(0)

                server_socket.listen()
                web_socket.listen()

                chats = ChatCollection(30)
                print(f"Terminal Clients: listening on machine {socket.gethostname()} and on port {PORT}")
                print(f"WEB Clients: listening on machine {socket.gethostname()} and on port {WEB_PORT}")

                
                try:
                    with open(sys.argv[1],'r') as file:
                        lines = file.readlines()
                        for i in range(len(lines)):
                            chats.add_client_message(lines[i],time.time())
                except FileNotFoundError:
                    print(f"Creating a file named {sys.argv[1]}")

                with open(sys.argv[1],'a+') as dataBase:
                    select_part(server_socket,web_socket,dataBase,chats)
                

        else:
            print("Please Enter the filename if a file doesn't exist it will be created.")
                    


main()
