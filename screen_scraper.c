#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <assert.h>
#include <stdlib.h>
#include <netdb.h>


char* make_request(char request[],struct sockaddr_in server_addr,char* server_response,int response_size){
      int socket_desc = socket(AF_INET,SOCK_STREAM,0);
      //connect to the server 
      if(connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
        printf("Unable to connect\n");
        return NULL;
    }

    // send the request 
    if(send(socket_desc,request, strlen(request), 0) < 0){
        printf("Unable to send message\n");
        close(socket_desc);
        return NULL;
    }
   

    int recieved_bytes = recv(socket_desc, server_response,response_size-1, 0);
     // Receive the server's response:
    if(recieved_bytes < 0){
        printf("Error while receiving server's msg\n");
        close(socket_desc);
        return NULL;
    }

    if(recieved_bytes < (response_size-1)){
        server_response[recieved_bytes] = '\0';
    }else{
        server_response[response_size-1]='\0';
    }

    close(socket_desc);
    return server_response;


}

int main(int argc, char *argv[])
{
    if(argc < 5)
    {
        printf("Please enter HOST PORT USERNAME MESSAGE as a command line argument\n");
        return -1;
    }


    char* HOST =  argv[1];
    char* PORT_string = argv[2];
    int PORT = atoi(PORT_string);
    char* username =  argv[3];
    char* message;

    size_t total_length = 1; //counting the null terminator 
    //read the entire message 
    for(int i=4; i < argc-1; i++)
    {
        total_length += strlen(argv[i]);
        total_length += strlen(" ");
    }

    total_length += strlen(argv[argc-1]);

    //allocate space to hold the entire message.
    message = malloc(total_length);

    if(message == NULL)
    {
        printf("Memory allocation failed\n");
        return -1;
    }

    message[0] = '\0';

    //concatencate all the words
    for(int i=4; i < argc-1; i++)
    {
        strcat(message,argv[i]);
        strcat(message," "); //add the space.
    }
    
    //no space needed after the end word
    strcat(message,argv[argc-1]);

    //make sure the port number is a valid number 
    if(PORT  == 0)
    {
        printf("Please enter a valid PORT number\n");
        return -1;
    }
    
    char json_content[4000]; //content that is going to be sent.
    sprintf(json_content, "{\"username\":\"%s\",\"message\":\"%s\"}",username,message);

    //these are used to check the status codes
    const char *sucess_status = "HTTP/1.1 200 OK";
    const char *unauthorized_status= "HTTP/1.1 401 Unauthorized";
    const char *error_message = "Not logged In";
    

    struct sockaddr_in server_addr;
    char server_message[4000];


    //initialize the addrInfo structs
    struct addrinfo hints,*res;
    memset(&hints,0,sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM; //TCP socket

    int status = getaddrinfo(HOST,PORT_string,&hints,&res);
    
    if(status != 0)
    {
        printf("ERROR: getaddrINFO!\n");
        return -1;
    }
  
   //get the resolved address(the first address in the list)
   struct sockaddr_in *ipv4 = (struct sockaddr_in*)res->ai_addr;
   server_addr = *ipv4;


    // Clean buffer:
    memset(server_message,'\0',sizeof(server_message));
    
    printf("Requesting /api/messages...\n");
    //get all the messages. With a cookie to simulate the logging in process
    char first_request[4000];
    sprintf(first_request,"GET /api/messages HTTP/1.1\r\nCookie: username=%s\r\n\r\n",username);
  
    //get all the messages first
    char* returned = make_request(first_request,server_addr,server_message,sizeof(server_message));
    if(returned == NULL)
    {
        return -1;
    }
    
    //assert the status is 200 OK by comparing the first few words of the server's response
    assert(strncmp(server_message,sucess_status,strlen(sucess_status)) == 0);
     printf("The status code is 200 OK\n");

    //assert that the message is not in the response.
    assert(strstr(server_message,message)==NULL);
     printf("The message \'%s\' has not been found in the response\n",message);
  

    printf("Server's response:\n %s\n",server_message);
    printf("------------------------------------------\n");
   
    printf("Sending Post request to the server.....\n");
   
    int json_length = strlen(json_content); 
    char second_request[6000];
    sprintf(second_request, "POST /api/messages HTTP/1.1\r\nCookie: username=%s\r\nContent-Length: %d\r\n\r\n%s",username,json_length, json_content);

    //clear the buffer 
    memset(server_message,'\0',sizeof(server_message));

   returned = make_request(second_request,server_addr,server_message,sizeof(server_message));
   if(returned == NULL)
    {
        return -1;
    }
    //assert the status is 200 OK
    assert(strncmp(server_message,sucess_status,strlen(sucess_status)) == 0);
    printf("The status code is 200 OK\n");

    printf("Server's response:\n %s\n",server_message);
    printf("------------------------------------------\n");
    
    printf("Requesting /api/messages/...again\n");
    
    //clear the buffer 
    memset(server_message,'\0',sizeof(server_message));

    returned = make_request(first_request,server_addr,server_message,sizeof(server_message));
    if(returned == NULL)
    {
        return -1;
    }

     //assert the status is 200 OK by comparing the first few words of the server's response
    assert(strncmp(server_message,sucess_status,strlen(sucess_status)) == 0);
    printf("The status code is 200 OK\n");
    //assert that the message is the response.
    assert(strstr(server_message,message)!=NULL);
    printf("The message \'%s\' has been found in the response\n",message);

    printf("Server's response:\n %s\n",server_message);

    printf("------------------------------------------\n");
    
    printf("Attempting to request Get /api/messages when not logged in.....\n");
    //this request has no cookie.
    char third_request[] =  "GET /api/messages HTTP/1.1\r\n\r\n";
    //clear the buffer 
    memset(server_message,'\0',sizeof(server_message));

    returned = make_request(third_request,server_addr,server_message,sizeof(server_message));
    if(returned == NULL)
    {
        return -1;
    }

    //make sure the status code is 401 unauthorized
    assert(strncmp(server_message,unauthorized_status,strlen(unauthorized_status)) == 0);
    printf("The status code is 401 unauthorized\n");
    //assert that their is an error message
    assert(strstr(server_message,error_message)!=NULL);
    printf("A good error message has been found\n");

    printf("Server's response:\n %s\n",server_message);

    printf("Attempting to request POST /api/messages when not logged in.....\n");
    //this request has no cookie.
    char fourth_request[6000];
    //the request has no cookie
    sprintf(fourth_request, "POST /api/messages HTTP/1.1\r\nContent-Length: %d\r\n\r\n%s", json_length, json_content);

    //clear the buffer 
    memset(server_message,'\0',sizeof(server_message));

    returned = make_request(fourth_request,server_addr,server_message,sizeof(server_message));
    if(returned == NULL)
    {
        return -1;
    }

    //make sure the status code is 401 unauthorized
    assert(strncmp(server_message,unauthorized_status,strlen(unauthorized_status)) == 0);
    printf("The status code is 401 unauthorized\n");
    //assert that their is an error message
    assert(strstr(server_message,error_message)!=NULL);
    printf("A good error message has been found\n");

    printf("Server's response:\n %s\n",server_message);

    printf("Finished Scrapping!\n");
    free(message);
    return 0;
}