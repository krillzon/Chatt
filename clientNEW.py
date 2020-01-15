#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
import socket
from socket import AF_INET, SOCK_STREAM
from threading import Thread
from tkinter import *
import requests, json
from datetime import datetime

firstclick = True
HOST = "127.0.0.1"
PORT = 33002


#TODO
# Remove being able to close chat on X
# Can print all online Clients
# Time
def message_box(event):
    """function that gets called whenever someone clicks the entry fields for the first time"""
    global firstclick

    if firstclick: # if this is the first time they clicked it
        firstclick = False
        yourMessage.delete(0, "end") # delete all the text in the entry


def get_dad_joke():
    resp = requests.get("https://us-central1-dadsofunny.cloudfunctions.net/DadJokes/random/jokes")
    resp_json = json.loads(resp.text)
    return resp_json['setup'], resp_json['punchline']


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            #data = client_socket.recv(BUFSIZ).decode("utf8")
            data = client_socket.recv(BUFSIZ).decode("utf8")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if len(data) == 0:
                pass
            else:
                messageHistory.insert(END,'\n', now, data)
                messageHistory.see("end")
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):
    message = my_msg.get()
    part2 = ''
    if my_msg.get() == "!dad":
       (message, part2) = get_dad_joke()
    my_msg.set('')  # Clears input field.
    try:
        if message[0] == '/' or message[0] == '-' or 'quitchat' in message:
            client_socket.send(bytes(message, "utf-8"))
        else:
            client_socket.send(bytes((message), "utf-8"))
            if part2 != '':
                client_socket.send(bytes((part2), "utf-8"))
    except ConnectionResetError:
        pass
    if message == "quitchat":
        client_socket.close()
        root.quit()

def on_closing(event=None):
    """This function is to be called when the window is closed."""
    #client_socket.close()
    #root.quit()
    my_msg.set("quitchat")
    send()


root = Tk()
root.title("Connected to " + HOST + ":" + str(PORT) )

my_msg = StringVar()  # For the messages to be sent.
my_msg.set("Type your username here, and then you can start chatting!")
# Following will contain the messages.
messageHistory = Listbox(master=root, width=120, height=20)
messageHistory.pack(expand=True, fill=BOTH)

messages_frame = Frame(root)
messages_frame.pack()

yourMessage = Entry(root, textvariable=my_msg, width=50)
yourMessage.bind('<FocusIn>', message_box)
yourMessage.bind("<Return>", send)
yourMessage.pack(expand=True, fill="x")

send_button = Button(root, text="Send", command=send)
send_button.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

#----Socket code----
#HOST = input('Enter host: ')
#PORT = input('Enter port: ')
#if not PORT:
#    PORT = 33002
#else:
#    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket.socket(AF_INET, SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
root.mainloop()