import json 

class Chat:
    def __init__(self,time,username,message,id):
        self.__time = time
        self.__username = username
        self.__message = message
        self.__id = id

    def get_id(self):
        return self.__id
    
    def get_time(self):
        return self.__time
    
    def get_username(self):
        return self.__username
    
    def get_message(self):
        return self.__message
    
    def __str__(self):
        return self.__username +":"+self.__time+":"+self.__message+'\n'
    
class ChatCollection:
    def __init__(self,num_messages:int):
        self.__chats = []
        self.__retain = num_messages
        self.__id = 0

    def add_client_message(self,message,time):
        message = message.split(':')
        #matches our message protocol
        username=''
        chat=''
        if(len(message)>=2):
            username = message[0]
            #there might be more than one occurence of :
            for i in range(1,len(message)):
                chat += message[i]
        #else:
            #username = "Guest"
            #chat = message[0]
        self.__id+=1
        self.__chats.append(Chat(time,username,chat,self.__id))

        if(len(self.__chats) > self.__retain):
            self.__chats = self.__chats[-self.__retain:]

        
                
    def add_web_message(self,message,time):
            self.__id += 1
            self.__chats.append(Chat(time,message.get('username',"NONE"),message.get("message","NONE"),self.__id))

    def get_all_messages(self):
        return self.__chats.copy()
    
    #return all messages greater than id
    def get_all_messages(self,id:int):
        messages = []
        for i in range(len(self.__chats)):
            curr_chat:Chat = self.__chats[i]
            if(curr_chat.get_id() > id):
                messages.append(curr_chat)
        
        return messages
    
    def delete_messages(self,username):
        copyMessages = self.get_all_messages(0)
        #iterate backwards...
        for i in range(len(self.__chats) - 1, -1, -1):
            if self.__chats[i].get_username() == username:
                copyMessages.remove(copyMessages[i])
        self.__chats = copyMessages

    
    def __str__(self):
        toReturn = ""
        for i in range(len(self.__chats)):
            toReturn += self.__chats[i]
        return toReturn 