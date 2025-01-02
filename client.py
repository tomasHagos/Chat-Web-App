import socket
import sys
import select


def select_part(s,user_name):
    isExit = False
    while not isExit:
        try:
            inputs = [sys.stdin,s]
            readable,writable,exceptional = select.select(inputs,[],inputs)
                    
            for item in readable:
                if(item is sys.stdin):
                    data = sys.stdin.readline().strip() #remove the \n
                    #check if the client is exiting.
                    if data.lower() == "exit":
                        isExit = True
                    else:
                        sent_data = user_name + ": "+data
                        s.sendall(sent_data.encode())
                if(item is s):
                    try:
                        data= s.recv(6144)
                        if not data:
                            print("Goodbye")
                            sys.exit(0)
                        else:
                            data = data.decode('utf-8')
                            data = data.split('\n')
                            for i in range(len(data)):
                                print(data[i].strip())
                            #use carriage return to overwrite the user's input
                            #it moves the cursor to the beginning of the line
                            #print("\r" + data.decode('utf-8').strip())
                    except OSError as e:
                        pass

        except KeyboardInterrupt as e:
            print("Goodbye")
            sys.exit(0)
        except Exception as e:
            print(f"Something has happened: {e}")
            sys.exit(0)


def main():
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if(len(sys.argv) >=4):
            user_name = sys.argv[1]
            HOST = sys.argv[2]
            PORT = int(sys.argv[3])
            try:
                s.connect((HOST,PORT))
                print("Succesfully Connected!")
                s.settimeout(0) #make the recv and send none blocking since we are using select
                select_part(s,user_name)
            except socket.error as e:
                print(f"Failed to connect to the server:{e}")
        else:
            print("Please enter USERAME HOST PORT as the command line argument")

        print("Goodbye!")


#wrapper(main)
main()
#data = "something"
  # while data != "exit":
    #   data = input("Send a message to the server:")
     #  s.sendall(data.encode('utf-8'))