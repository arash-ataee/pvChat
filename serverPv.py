import socket
import time
import select
import sqlite3
from sqlite3 import Error
import datetime


def create_connection(db_file):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return connection


def create_table(connection, create_table_sql):
    try:
        c = connection.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_user(connection, u):
    sql = ''' INSERT INTO users(name,socket,status)
              VALUES(?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, u)
    return cur.lastrowid


def create_chat(connection, ch):
    sql = ''' INSERT INTO chats(sender_name,receiver_name,chat_time)
              VALUES(?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, ch)
    return cur.lastrowid


database = r"pvchat.db"

sql_create_users_table = """ CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    name text NOT NULL,
                                    socket text NOT NULL,
                                    status text NOT NULL
                                ); """

sql_create_chats_table = """CREATE TABLE IF NOT EXISTS chats (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                sender_name text NOT NULL,
                                receiver_name text NOT NULL,
                                chat_time text NOT NULL
                            );"""

conn = create_connection(database)

if conn is not None:
    create_table(conn, sql_create_users_table)

    create_table(conn, sql_create_chats_table)
else:
    print("Error! cannot create the database connection.")


IP = 'localhost'
PORT = 8000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

server_socket.listen(10)
print("server up!")

socket_list = [server_socket]

clients = {}
audiences = {}

while True:
    read_socket, write_socket, exception_socket = select.select(
        socket_list, socket_list, socket_list)
    for s in read_socket:
        if s == server_socket:
            client_socket, address = server_socket.accept()
            if client_socket:
                # client_socket.send(bytes("welcome!", 'utf-8'))
                socket_list.append(client_socket)
                print("Connection Established from {}".format(address))
    for s in read_socket:
        if s not in clients.values():
            username = None
            try:
                username = s.recv(1024).decode('utf-8')
            except IOError:
                continue
            if username:
                if username in clients:
                    s.send(bytes('error1', 'utf-8'))
                if username not in clients:
                    s.send(bytes('accept1', 'utf-8'))
                    clients[username] = s
                    with conn:
                        user = (username, str(s), 'online')
                        create_user(conn, user)
                    names = ''
                    for name in list(clients.keys()):
                        names += name + ' '
                    s.send(bytes(names, 'utf-8'))
                    print(clients)
                    print(audiences)
        else:
            message = None
            try:
                message = s.recv(1024).decode('utf-8')
            except IOError:
                continue
            if message:
                if message.startswith('adnc'):
                    audience = message[4:]
                    if audience in audiences:
                        if audiences[audience] != s:
                            s.send(bytes('error2', 'utf-8'))
                            message = None
                        else:
                            s.send(bytes('accept2', 'utf-8'))
                            message = None
                    else:
                        s.send(bytes('accept2', 'utf-8'))
                        audiences[s] = audience
                        audiences[audience] = s
                        message = None
                if message:
                    sender_name = list(clients.keys())[list(clients.values()).index(s)]
                    receiver_name = audiences[s]
                    chat_time = datetime.datetime.now()
                    chat = (sender_name, receiver_name, str(chat_time))
                    with conn:
                        create_chat(conn, chat)
                    clients[receiver_name].send(
                        bytes(sender_name + ': ' + message + '\n', 'utf-8'))

    for s in exception_socket:
        socket_list.remove(s)
        del clients[s]
        del audiences[audiences[s]]
        del audiences[s]

    time.sleep(1)
    # print(socket_list)
# server_socket.close()
