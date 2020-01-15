#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import socket
from socket import AF_INET, SOCK_STREAM
import threading
from threading import Thread
import sys, requests, json, sqlite3
from datetime import datetime
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

#TODO
# Tkinter window
# Print server messages
# Print TrainInfo
#

# AN CLIENT THAT SENDS INFO AUTO
def train_announcement():
    sent = True
    while True:
        if int(datetime.now().strftime('%M')) % 2 == 0 and not sent:
            resp = requests.get(f"http://api.sl.se/api2/realtimedeparturesV4.json?key=b0c3cced0bba45c58222712c148b6cf2&siteid=9633&timewindow=10")
            my_json = json.loads(resp.text)
            if my_json['ResponseData']['Trams'][0]['DisplayTime'] != "Nu":
                broadcast(bytes(f"SERVER: next train to {my_json['ResponseData']['Trams'][0]['Destination']} leaves in {my_json['ResponseData']['Trams'][0]['DisplayTime']} or {my_json['ResponseData']['Trams'][1]['Destination']} {my_json['ResponseData']['Trams'][1]['DisplayTime']}", 'utf-8'))
            sent = True
        elif int(datetime.now().strftime('%M')) % 2 != 0 and sent:
            sent = False


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Please enter your name in the textbox!!", "utf8"'\n'))
        client.send(bytes("To close the chat you can either type quitchat or force close it.", "utf8"))

        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZE).decode("utf8")
    welcome = 'Welcome %s!, type quitchat to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZE)
        print(name, "says", msg)
        #To get all client info you can print client
        #print(client)
        if msg != bytes("quitchat", "utf8"):
            broadcast(msg, name + ": ")
        else:
            del clients[client]
            #Om det inte finns clients kvar, stäng servern, annars broadcasta att personen lämnade
            if len(clients) == 0:
                SERVER.close()
                sys.exit(0)
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            #print("%s has been deleted from the Database!" % name)

            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


clients = {}
addresses = {}

HOST = ''
PORT = 33002
BUFSIZE = 1024

if __name__ == "__main__":

    #Create a database connection or create one
    messages_conn = sqlite3.connect('message_history.db')
    messages_cursor = messages_conn.cursor()

    ADDR = (HOST, PORT)
    SERVER = socket.socket(AF_INET, SOCK_STREAM)
    SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SERVER.bind(ADDR)
    SERVER.listen(5)
    print("Server running...")
    print("Ready to take in clients!")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    #for client to send message random
    threading.Thread(target=train_announcement).start()
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()

    messages_conn.close()
    messages_cursor.close()

    SERVER.close()
