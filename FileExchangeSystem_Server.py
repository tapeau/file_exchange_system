# Machine Project Group 10
# TAPIA, John Lorenzo N.
# ARGAMOSA, Daniel Cedric S.

import socket
import time
import json
import ipaddress
import os
from datetime import datetime

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP Socket 
buffer = 4096  # buffer for files and messages
server_directory = os.path.abspath("ServerFolder")

# to display time logs
time_format = "%Y-%m-%d %H:%M:%S"
current_time = datetime.now().strftime(time_format)

clients = {} # Client address and alias list {address: alias}, the alias gets added on in a different command
disconnected_clients = [] # Client address list of disconnected clients

# Pings the connected clients for validation when a connection error occurs
def ping():
    for user in clients:
        print(f"Pinging user {user} : ", end="")
        ping_req = {'command': 'ping'}
        server_socket.sendto(json.dumps(ping_req).encode(), user) # ping if still connected
        time.sleep(0.3)
        try:
            server_socket.recvfrom(buffer)
            print("ONLINE") # prints when connected
        except:
            print("OFFLINE")
            disconnected_clients.append(user)

def validIP(serverIP):
    try:
        ipaddress.ip_address(serverIP)
        return True
    except socket.error:
        return False

def validPort(nServerPort):
    try:
        port_num = int(nServerPort)
        return 0 < port_num < 65536  # Because the port range is 1-65535
    except ValueError:
        return False

# Processes commands received from clients
def processClients(userInput):
    message = json.loads(userInput.decode())
    command = message['command'] 
    

        # ip = message['ip']
        # port = message['port'] 

        # try:
        #     # Attempt to create a temporary socket and connect to the provided IP and port
        #     test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     test_socket.settimeout(3)  # Checks to see if it exists
        #     test_socket.connect((ip, port))
        #     test_socket.close()  # Close the test socket if connection successful

        #     # Connection successful
        #     connectionState = True

        # except socket.timeout:
        #     # Connection attempt timed out
        #     connectionState = False

        # if connectionState is False:
        #     print(f"[{current_time}] ({address}) attempted connection")
        #     jsonData = {'command': 'error', 'message': "ERROR: No server with that ip and port exists"}
        # else:

     # A client joins the server
    if command == "join":
        clients.update({address : None})
        print(f"[{current_time}] Client with IP Address: {address} has connected to the server")
        jsonData = {'command': 'all', 'message': f"A user at {address} has connected to the server"}

        # Messages other connected users
        for client_address, alias in clients.items():
            if client_address != address:
                if alias is not None:  # Only sends the message to registered clients
                    server_socket.sendto(json.dumps(jsonData).encode(), client_address)
    
    # A client leaves the server
    elif command == "leave":
        print(f"[{current_time}] Client {clients[address]}:{address} has disconnected from the server")
        if clients[address] is None:
            message = "Unregistered user disconnected from the server"
        else:
            message = f"User {clients[address]} disconnected from the server"
        jsonData = {'command': 'all', 'message': message}

        # Deletes it in the list
        del clients[address]

        for client_address, alias in clients.items():
            if client_address != address:
                if alias is not None:  # Only sends the message to registered clients
                    server_socket.sendto(json.dumps(jsonData).encode(), client_address)
    
    # A client attempts to register
    elif command == "register":
        alias = message['alias']
        
        # If they are registered already
        if clients[address] != None:
            print(f"[{current_time}] Client ({clients[address]}) attempted re-registration")
            jsonData = {'command': 'error', 'message': "ERROR: You are already registered in the system"}
        # If another client has registered with that name
        elif alias in clients.values():
            print(f"[{current_time}] Client ({clients[address]}) alias registration failed")
            jsonData = {'command': 'error', 'message': f"ERROR: {alias} is already taken in this server"}
        else:
            clients[address] = alias
            print(f"[{current_time}] You have successfully registered to the server with the alias: {alias} at {address}")
            jsonData = {'command': 'success', 'given' : 'register' , 'message': f"Welcome to the server {alias}!"}
            jsonData2 = {'command': 'all', 'message': f"A user registered with the alias: {alias} at {address}"}
            for client_address, alias in clients.items():
                if client_address != address:
                    if alias is not None:  # Only sends the message to registered clients
                        server_socket.sendto(json.dumps(jsonData2).encode(), client_address)
        server_socket.sendto(json.dumps(jsonData).encode(), address)
    
    # Display the contents of the server folder
    elif command == "dir":
        print(f"[{current_time}] Client {clients[address]} has requested to see the available server files")
        # Name of where server files are stored
        filelist = os.listdir('ServerFolder')

        if not filelist:
            # If the directory is empty
            jsonData = {'command': 'error', 'message': f"There are no files currently saved in this Server"}
            server_socket.sendto(json.dumps(message).encode(), address)
        else:
            jsonData = {'command': 'success', 'message': f"Here are the list of files: {filelist}!"}
            jsonData2 = {'command': 'all', 'message': f"Client {clients[address]} sees the server files"}

            for client_address, client_alias in clients.items():
                if client_address != address:
                    if client_alias is not None:  # Only sends the message to registered clients
                        server_socket.sendto(json.dumps(jsonData2).encode(), client_address)

        server_socket.sendto(json.dumps(jsonData).encode(), address)

    # A client attempts to download a file
    elif command == "get":
        filename = message['filename']
        filelist = os.listdir('ServerFolder')
        
        # If the requested file is not within the server folder
        if filename not in filelist:
            print(f"[{current_time}] Client ({clients[address]}) attempts to download a file that does not exist")
            jsonData = {'command': 'error', 'message': "ERROR: There are no files in the server with that name"}
        else:
            try:
                print(f"[{current_time}] Client {clients[address]} has downloaded file '{filename}'")
                jsonData = {'command': 'success', 'message': f"'{filename}' has been downloaded successfully in your default Downloads folder"}
                jsonData2 = {'command': 'all', 'message': f"Client {clients[address]} has downloaded file '{filename}'"}
            
            except Exception as e:
                print(f"Error downloading file '{filename}': {str(e)}")
                jsonData = {'command': 'error', 'message': f"Error downloading file '{filename}'"}
                server_socket.sendto(json.dumps(jsonData).encode(), address)
            
            for client_address, alias in clients.items():
                if client_address != address:
                    if alias is not None:  # Only sends the message to registered clients
                        server_socket.sendto(json.dumps(jsonData2).encode(), client_address)
        server_socket.sendto(json.dumps(jsonData).encode(), address)

    elif command == "store":
        filename = message['filename']
        
        # If the file being sent doesn't exist
        if not os.path.exists(filename):
            print(f"[{current_time}] Client ({clients[address]}) attempts to upload a file that does not exist")
            jsonData = {'command': 'error', 'message': "ERROR: File does not exist. Check your directory"}
        else:
            try:
                print(f"[{current_time}] Client {clients[address]} has uploaded file '{filename}'")
                jsonData = {'command': 'success', 'message': f"'{filename}' has been uploaded successfully into the Server"}
                jsonData2 = {'command': 'all', 'message': f"Client {clients[address]} has uploaded file '{filename}'"}
            
            except Exception as e:
                print(f"Error uploading file '{filename}': {str(e)}")
                jsonData = {'command': 'error', 'message': f"Error uploading file '{filename}'"}
                server_socket.sendto(json.dumps(jsonData).encode(), address)
            
            for client_address, alias in clients.items():
                if client_address != address:
                    if alias is not None:  # Only sends the message to registered clients
                        server_socket.sendto(json.dumps(jsonData2).encode(), client_address)
        server_socket.sendto(json.dumps(jsonData).encode(), address)

    # Send message to all
    elif command == "all":
        
        print(f"[{current_time}] Client ({clients[address]}) sends a message to all")
        message = f"{clients[address]}: {message['message']}"
        print(f"{address} > {message}")
        message_data = {'command': 'all', 'message': message}
        for client_address, alias in clients.items():
            if alias is not None:  # Only sends the message to registered clients
                server_socket.sendto(json.dumps(message_data).encode(), client_address)
    
    # Send direct message
    elif command == "msg":
        alias = message['alias']
        message = message['message']
        sender = clients[address]
        
        if clients[address] == alias:
            print(f"Client {clients[address]} attempted /msg to themselves")
            jsonData = {'command': 'error', 'message': "ERROR: You cannot message yourself"}
            server_socket.sendto(json.dumps(jsonData).encode(), address)
            return
        
        for client_address, handle in clients.items():
            if handle == alias:
                message_data = {'command': 'msg', 'alias': sender, 'message': message}
                try:
                    server_socket.sendto(json.dumps(message_data).encode(), client_address)
                    print(f"Message from {address} to {client_address}")
                    message = f"[To {alias}]: {message}"
                    jsonData = {'command': 'success', 'given' : 'msg' , 'message': message}
                except:
                    server_socket.sendto(json.dumps(jsonData).encode(), address)
                    jsonData = {'command': 'error' , 'message': "ERROR: Alias not found"}
                server_socket.sendto(json.dumps(jsonData).encode(), address)  
                return
        print(f"Direct message by {address} to alias {alias} failed")
        jsonData = {'command': 'error' , 'message': "ERROR: Alias not found"}
        server_socket.sendto(json.dumps(jsonData).encode(), address)

print("------------------------------")
print("FILE EXCHANGE SYSTEM - SERVER")
print("------------------------------")
print("Welcome!\n")
# Server loop
while True:
    try:
        # Declare variables
        while True:
            serverIP = input("Please enter the server IP address: ")
            if validIP(serverIP):
                break
            else:
                print("ERROR: Invalid IP address format. Please enter a valid IPv4 address.\n")

        while True:
            nServerPort = input("Please enter a port number to be used by the server: ")
            if validPort(nServerPort):
                break
            else:
                print("ERROR: Invalid port number. Please enter a valid port in the range 1-65535.\n")

        # Establish server socket
        server_socket.bind((serverIP, int(nServerPort))) 
        print(f"[{current_time}] Server running at {serverIP}:{nServerPort} - Listening to port {nServerPort}")
        break
    except Exception as e:
        print(f"ERROR: {str(e)}\n")

# This loop checks client activities
while True:
    try: 
        userInput, address = server_socket.recvfrom(buffer)
        processClients(userInput)
    
    except ConnectionResetError as e: # Abrupt disconnects
        print(f"ConnectionResetError: {e}")  
        ping()   
            
    except Exception as e: # Other errors
        print(f"Error: {e}")
    
    finally: # Always runs per loop
        for user in disconnected_clients:
            print(f"User {clients[user]} : {user} offline. Disconnecting")
            clients.pop(user)
        disconnected_clients.clear()