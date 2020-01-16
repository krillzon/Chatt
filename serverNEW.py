#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import socket, threading, sys, requests, json, sqlite3
from socket import AF_INET, SOCK_STREAM
from threading import Thread
from datetime import datetime, date
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

#TODO
# Kommentera koden
#


def create_table(now):
    messages_cursor.execute(f"CREATE TABLE IF NOT EXISTS {now.strftime('%B_%d_%Y')}(date TEXT, user TEXT, message TEXT)")


def messages(now, date_format, user, msg):
    messages_cursor.execute(f"INSERT INTO {now.strftime('%B_%d_%Y')}(date, user, message) VALUES (?, ?, ?)",
                      (date_format, user, msg))
    messages_conn.commit()


# AN CLIENT THAT SENDS INFO AUTO
def train_announcement():
    has_sent = True
    while True:
        if int(datetime.now().strftime('%M')) % 2 == 0 and not has_sent:
            resp = requests.get(f"http://api.sl.se/api2/realtimedeparturesV4.json?key=b0c3cced0bba45c58222712c148b6cf2&siteid=9633&timewindow=30")
            my_json = json.loads(resp.text)
            if my_json['ResponseData']['Trams'][0]['DisplayTime'] != "Nu":
                broadcast(bytes(f" Next train to {my_json['ResponseData']['Trams'][0]['Destination']} leaves in {my_json['ResponseData']['Trams'][0]['DisplayTime']}", 'utf-8'))
                #or {my_json['ResponseData']['Trams'][1]['Destination']} {my_json['ResponseData']['Trams'][1]['DisplayTime']}", 'utf-8'))
            has_sent = True
        elif int(datetime.now().strftime('%M')) % 2 != 0 and has_sent:
            has_sent = False


def get_groups1(client, day):
    date = day.split()[1]
    messages_cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{date}'")
    if messages_cursor.fetchone()[0] == 1:
        messages_cursor.execute(f"SELECT * from {date} WHERE user LIKE '%1:%'")
        for row in messages_cursor.fetchall():
            try:
                messages_cursor.execute(f"SELECT user from {date}")
                client.send(bytes(f"{row[1]}", 'utf-8'))
            except ConnectionResetError:
                return
    else:
        client.send(bytes(f"{day.split()[1]} please insert: @geton [fullmonthname_date_fullyear]", 'utf-8'))


def get_groups2(client, day):
    date = day.split()[1]
    messages_cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{date}'")
    if messages_cursor.fetchone()[0] == 1:
        messages_cursor.execute(f"SELECT * from {date} WHERE user LIKE '%2:%'")
        for row in messages_cursor.fetchall():
            try:
                messages_cursor.execute(f"SELECT user from {date}")
                client.send(bytes(f"{row[1]}", 'utf-8'))
            except ConnectionResetError:
                return
    else:
        client.send(bytes(f"{day.split()[1]} please insert: @geton [fullmonthname_date_fullyear]", 'utf-8'))


def get_messages(client, day):
    date = day.split()[1]
    messages_cursor.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{date}'")
    if messages_cursor.fetchone()[0] == 1:
        messages_cursor.execute(f"SELECT * from {date}")
        for row in messages_cursor.fetchone():
            try:
                client.send(bytes(f"{row[0]} {row[1]}{row[2]}", 'utf-8'))
            except ConnectionResetError:
                return
    else:
        client.send(bytes(f"{date} please insert: -d [fullmonthname_date_fullyear]", 'utf-8'))


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        try:
            client, client_address = SERVER.accept()
        except:
            print("NO USERS CONNECTED, CLOSING THE SERVER")
            SERVER.close()
            sys.exit(0)

        print("%s:%s has connected." % client_address)
        client.send(bytes("Please enter your name in the textbox!!", "utf8"'\n'))
        client.send(bytes("To close the chat you can either type quitchat or force close it.", "utf8"))

        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def ask_group(client, name):

    if client.recv(BUFSIZE).decode("utf8") != "1":
        if client.recv(BUFSIZE).decode("utf8") != "2":
            client.send(bytes("Please enter a group between 1 or 2", 'utf8'))
            ask_group(client, name)
        else:
            group = client.recv(BUFSIZE).decode("utf8")
            letter = 'Welcome to group %s.' % group
            client.send(bytes(letter, "utf8"))
    else:
        group = client.recv(BUFSIZE).decode("utf8")
        letter = 'Welcome to group %s.' % group
        client.send(bytes(letter, "utf8"))


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZE).decode("utf8")
    onlineClients.append(name)
    welcomeletter = 'Welcome %s!' % name
    client.send(bytes(welcomeletter, "utf8"))
    client.send(bytes("Please enter your group", 'utf8'))

    ask_for_group = True
    while ask_for_group:
        if client.recv(BUFSIZE).decode("utf8") != "1":
            if client.recv(BUFSIZE).decode("utf8") != "2":
                client.send(bytes("Please enter a group between 1 or 2", 'utf8'))
            else:
                group = client.recv(BUFSIZE).decode("utf8")
                letter = 'Welcome to group %s.' % group
                newnamed = ''
                newname = name.join((newnamed, group))
                #client.send(bytes(newname, "utf8"))
                client.send(bytes(letter, "utf8"))
                ask_for_group = False
        else:
            group = client.recv(BUFSIZE).decode("utf8")
            letter = 'Welcome to group %s.' % group
            newnamed = ''
            newname = name.join((newnamed, group))
            #client.send(bytes(newname, "utf8"))
            client.send(bytes(letter, "utf8"))
            ask_for_group = False

    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
                msg = client.recv(BUFSIZE)
                print(name, "says", msg)
                if msg.decode('utf-8')[0] == '-':
                    if msg.decode('utf-8')[:6] == '-getdb':
                        str_message = msg.decode('utf-8')
                        if len(str_message.split()) == 2:
                            get_messages(client, str_message)
                        else:
                            client.send(bytes("SERVER: Please insert what date: strMONTH_intDAY_intYEAR", 'utf-8'))
                    else:
                        client.send(bytes("SERVER: Maybe you meant: -getdb ?", 'utf-8'))

                if msg.decode('utf-8')[0] == '!':
                    client.send(bytes("SERVER: Commands are [ @getgp1, @getgp2, -getdb, /o, getdadjoke ]", 'utf-8'))
                elif msg.decode('utf-8')[0] == '@':
                    if msg.decode('utf-8')[:7] == '@getgp1':
                        groupie = msg.decode('utf-8')
                        if len(groupie.split()) == 2:
                            get_groups1(client, groupie)
                        else:
                            client.send(bytes("SERVER: Please insert date: strMONTH_intDAY_intYEAR", 'utf-8'))

                    elif msg.decode('utf-8')[:7] == '@getgp2':
                        groupie = msg.decode('utf-8')
                        if len(groupie.split()) == 2:
                            get_groups2(client, groupie)
                        else:
                            client.send(bytes("SERVER: Please insert date: strMONTH_intDAY_intYEAR", 'utf-8'))
                    else:
                        client.send(bytes("SERVER: Maybe you meant: @getgp1 or @getgp2?", 'utf-8'))

                elif msg.decode('utf-8')[0] == '/':
                    if msg.decode('utf-8')[:2] == '/o':
                        online = 'Online Clients %s' % onlineClients
                        #adressing = 'Online Adressses %s!.' % addresses
                        #client.send(bytes(adressing, "utf8"))
                        client.send(bytes(online, "utf8"))
                    else:
                        client.send(bytes("SERVER: Maybe you meant: /o ?", 'utf-8'))
                elif msg != bytes("quitchat", "utf8"):
                    broadcast(msg, newname + ": ")
                else:
                    del clients[client]
                    onlineClients.remove(name)
                    #Om det inte finns clients kvar, stäng servern, annars broadcasta att personen lämnade
                    if len(clients) == 0:
                        SERVER.close()
                        sys.exit(0)
                    broadcast(bytes("%s has left the chat." % name, "utf8"))
                    break


def broadcast(msg, prefix="Server: ", saved=True):
    """Broadcasts a message to all the clients."""
    time_time = datetime.now().strftime('[%Y-%m-%d|%H:%M:%S]')
    now = date.today()
    create_table(now)
    if saved:
        messages(now, time, prefix, msg.decode('utf-8'))
    for sock in clients:
        sock.send(bytes(time_time + prefix, "utf8") + msg)


onlineClients = []
clients = {}
addresses = {}

HOST = ''
PORT = 33002
BUFSIZE = 1024

if __name__ == "__main__":
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #Create a database connection or create one
    messages_conn = sqlite3.connect('message_history.db', check_same_thread=False)
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

    messages_cursor.close()
    messages_conn.close()

    SERVER.close()
