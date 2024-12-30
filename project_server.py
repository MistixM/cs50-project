# Server script

"""
    Server for multithreaded chat application

    We'll be using TCP instead of UDP sockets, because of TCP sockers are more telephonic.

    NOTICE! If server don't launch and raise 'PermissionError: [WinError 10013]' just 
    reboot network system.
    Using: 'net stop hns; net start hns' command in powershell (with admin permissions)
"""

from socket import AF_INET, socket, SOCK_STREAM # Import the socket library with AF_INET and SOCK_STREAM which can help to create the server side
from threading import Thread # Import Thread for multithreading
import customtkinter # For UI. NOTICE! This library should be installed
from tkinter import messagebox # Import tkinter for message boxes (because customtkinter does not support message boxes)
from PIL import Image # For working with images. Used in UI
import time # Time for better information in the server logs


def get_status(s): # REMOVE!
    return s

def main():
    # Set variables to global. Will use in future
    global SERVER, BUFSIZ, ACCEPT_THREAD, addresses, clients, app, status 

    # Create empty dicts to write all clients with their addresses
    clients = {}
    addresses = {}
    
    # Initialisate ui engine
    app = customtkinter.CTk()

    # Initialisate server information: Port and server status. Host is local by default.
    HOST = ''
    PORT = 2424
    BUFSIZ = 1024
    status = True

    ADDR = (HOST, PORT) # Create a tupple for server binding. Use one variable to represent the user address
    SERVER = socket(AF_INET, SOCK_STREAM) # Create server with AF_INET and SOCK_STREAM
    SERVER.bind(ADDR) # Connect address information
    SERVER.listen() # Listen all clients

    print("Waiting for connection..") # Just for debug

    ACCEPT_THREAD = Thread(target=accept_incoming_connections) # Start threading with current function

    ACCEPT_THREAD.start() # Start the loop
    draw_ui() # Start drawing ui
    
    ACCEPT_THREAD.join() # Main script should waits for Thread complete and doesn't jump to next line
    SERVER.close() # After stop threding, stop server

# Function, that briefly draws the ui
def draw_ui():
    global logs # Set to global logs variable (UI Frame)

    # Function that called when the user closes the window
    def on_closing(event=None):
        global status # Set global status variable
        # Ask the user if he is sure
        confirm = messagebox.askyesno("Server shutdown","This action will cause the server to stop. Are you sure?")
        # If user wants to exit, shutdown server and destroy ui
        if confirm:
            for client in clients:
                client.send(bytes("SHUTDOWN", "utf-8"))

            app.destroy()
            status = False
            
            SERVER.close()
            print("Server was closed")
    # Draw UI with specified methods
    app.geometry("600x300")
    app.resizable(False, False)
    app.title("Server launcher")
 
    # Contain log messages

    logs = customtkinter.CTkScrollableFrame(app, height=200, width=550)
    logs.pack(side=customtkinter.BOTTOM, pady=10)
    
    # Logs label (to inform the user host) and pack
    start_msg = customtkinter.CTkLabel(logs, 
                                       height=10, 
                                       width=logs.cget("width"), 
                                       anchor="nw", 
                                       text=f"{time.strftime('%H:%M:%S', time.localtime())} - Waiting for connection.."
                                       )
    start_msg.pack()

    # Stop server button with command specified function
    stop_server = customtkinter.CTkButton(app, 
                                          width=30, 
                                          height=30, 
                                          text="", 
                                          image=customtkinter.CTkImage(dark_image=Image.open("power.png"), 
                                          size=(20, 20)), 
                                          command=on_closing, 
                                          fg_color="#FFFFFF", 
                                          hover_color="#F0F0F0"
                                          )
    # Pack and place button
    stop_server.pack(side="left", anchor="s", padx=12)
    # Set protocol with specified function, when user wants to close the window
    app.protocol("WM_DELETE_WINDOW", on_closing)

    # UI loop
    app.mainloop()

# Function, that briefly accept clients to the server and types who has joined in the server logs
def accept_incoming_connections():
    global client_address # Set client_address to global variable
    while status: # Start loop with checking server status
        try: # Try to accept incoming clients
            client, client_address = SERVER.accept()
        except OSError: # But catch error when thing go wrong and break loop
            break
            
        # Create info label with information text (time and which client joined)
        info = customtkinter.CTkLabel(logs, 
                                      height=0, 
                                      width=logs.cget("width"), 
                                      anchor="nw", 
                                      text=f"{time.strftime('%H:%M:%S', time.localtime())} - {client_address} has connected."
                                      )
        info.pack()

        # After successful acceptance, write client to our dict
        addresses[client] = client_address

        # Start handle_client with the required attributes
        Thread(target=handle_client, args=(client,)).start()

# Function, that briefly handles client and communicates with the client
def handle_client(client):
    # Initialise user name
    name = client.recv(BUFSIZ).decode("utf-8")
    # Create welcome message
    welcome = f'Server: Welcome {name}! If you ever want to quit, type "quit" to exit the program.'
    # Try send to client welcome message in utf-8 encoding
    try:
        client.send(bytes(welcome, "utf-8"))
    # If connection is lost, catch error and close client
    except ConnectionResetError:
        client.close()

    # Create a message informing who has joined the chat
    msg = f"{name} has joined the chat."
    # Using broadcast function send 'join message'
    broadcast(bytes(msg, "utf-8"))
    # Insert user name to our dict
    clients[client] = name

    # Start the infinite loop responsible for sending the message
    while True:
        # Try to recieve client messages
        try:
            msg = client.recv(BUFSIZ)

        except (ConnectionResetError, OSError):
            '''
                Catch Connect and OS (problems with socket) errors. 
                Close client and clean up data. Send 'bye' information to other users in the chat. 
                Break loop      
            '''

            client.close()
            del clients[client]
            broadcast(bytes(f"{name} has left the chat.", "utf-8"))
            break

        # Also check if message is not /quit command
        if msg != bytes("/quit", "utf-8"):
            broadcast(msg, name + ": ")
        # Otherwise send to client /quit command message with client exit
        else:
            try:
                client.send(bytes("/quit", "utf-8"))
            # If program catch Connection error, close client, break the loop and clean up the data
            except ConnectionResetError:
                client.close()
                del clients[client]
                broadcast(bytes(f"{name} has left the chat.", "utf-8"))
                # We also tell in the server logs who is leaving with the given name 
                info = customtkinter.CTkLabel(logs, 
                                              height=0, 
                                              width=logs.cget("width"), 
                                              anchor="nw", 
                                              text=f"{time.strftime('%H:%M:%S', time.localtime())} - User: {name} with {client_address} has left the server!"
                                              )

                info.pack()
                break
            # We also record the name entered in the registration form (client side)
            if msg:
                name = msg.decode("utf-8")[5:]
            elif msg != bytes("/quit", "utf-8"):
                broadcast(msg, name + ": ")

# Function responsible for sending messages
def broadcast(msg, prefix=""): # prefix needs for name identification
    # Broadcast a message to all clients in the chat.
    for sock in clients:
        try:
            sock.send(bytes(prefix, "utf-8") + msg)
        except OSError:
            del clients[sock]

if __name__ == "__main__": 
    main()