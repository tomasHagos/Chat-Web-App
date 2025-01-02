# README


## PORT numbers:
I harded coded the port numbers since I found it to be easier that way. These ports numbers are assigned to me.

## First Step: Run the chat_server.py file
For terminal clients: uses port 8305

For web clients: uses port 8306 

Command to run chat_server.py: python3 chat_server.py filename.txt

If a filename exists it uses that, else it creates a txt file with that name.


## Second Step: Run the web_server.py file

The webserver uses the port mentioned above to access the chat_server.

The webserver uses PORT 8307 to listen web_clients. 

The webserver takes the HOST name of the chatserver as a command line argument.

Command to Run web_server.py

python3 web_server.py HOST(of the chatserver)

## How to run the client.py
command:python3 client.py username HOST(of the chat_server) 8305 

## Acessing the website

HOST(of the webserver):8307

## PART 2: Screen scrapper
Run: make

./screen_scrapper HOST(of the webserver) 8307 username message 

It prints the responses it gets. Also, it uses assert as specified. 

## favicon.oc file
I used an open source image that I got from the internet as the favicon. I have attached the file.

# Files folders

I also attached the files folder. It contains all the files(images,html,..)


# Others
I made the servers to print certain informations to the console to see what's going on behind the scenes.

I also made a class called chat.py that is in a different file.

# Additional Information
This web app can be simulated on localhost.

# Browser
Use google chrome. Safari has some issues with the cookies(to be fixed soon). 

# Pull Requests
Feel free to make pull requests

# Note
The socket only takes in 1024 bytes per call. This may crash if a large message is sent. This will be fixed soon.