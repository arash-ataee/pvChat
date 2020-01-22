from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import socket
import select
import threading
import time
import sys

IP = 'localhost'
PORT = 8000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.connect((IP, PORT))
server_socket.setblocking(False)

socket_list = [server_socket]

root = Tk()
root.title('arash chat')
root.resizable(False, False)


def chat_win():
    def receive():
        while True:
            read_socket, write_socket, excepted_socket = select.select(socket_list, socket_list, socket_list)
            for s in read_socket:
                r_message = s.recv(1024)
                if r_message:
                    chat_list.insert('end', r_message.decode('utf-8'))

                if not r_message:
                    socket_list.remove(s)
                    messagebox.showinfo(message="Connection Closed!", title='connection error')
            time.sleep(1)

    def send():
        message = message_var.get()
        chat_list.insert('end', 'you: ' + message)
        server_socket.send(bytes(message, 'utf-8'))

    chat_frame = ttk.Frame(root, padding=(50, 50, 62, 62))
    chat_frame.grid(column=0, row=0)
    chat_list = Listbox(chat_frame, height=10)
    chat_list.grid(column=1, row=1, sticky=(S, W, E, N))
    s = Scrollbar(chat_frame, orient=VERTICAL, command=chat_list.yview)
    s.grid(column=2, row=1, sticky=(N, S))
    chat_list['yscrollcommand'] = s.set
    message_var = StringVar()
    msg = Entry(chat_frame, width=20, textvariable=message_var)
    msg.grid(column=1, row=2)
    send_msg = Button(chat_frame, text='send', command=send)
    send_msg.grid(column=2, row=2)
    t1 = threading.Thread(target=receive)
    t1.start()


def match_win(audience_names):
    def aud():
        aud_name = audience_var.get()
        server_socket.send(bytes('adnc' + aud_name, 'utf-8'))
        error2 = None
        while not error2:
            try:
                error2 = server_socket.recv(1024).decode('utf-8')
            except IOError as e:
                continue
        if error2 == 'error2':
            return False
        if error2.startswith('accept2'):
            return True

    def aud_check():
        if aud():
            chat_win()
        else:
            messagebox.showinfo(message="the selected person is busy, select other person: ", title='audience error')

    match_frame = ttk.Frame(root, padding=(50, 50, 62, 62))
    match_frame.grid(column=0, row=0)
    name_label = Label(match_frame, text='select an online person: ')
    name_label.grid(column=1, row=1)
    audience_var = StringVar()
    audience = ttk.Combobox(match_frame, textvariable=audience_var)
    audience['values'] = audience_names.split()
    audience.grid(column=2, row=1)
    set_name = Button(match_frame, text='start chat', command=aud_check)
    set_name.grid(column=2, row=2)


def login_win():
    def login():
        user_name = username.get()
        server_socket.send(bytes(user_name, 'utf-8'))
        global error1
        error1 = None
        while not error1:
            time.sleep(1)
            try:
                error1 = server_socket.recv(1024).decode('utf-8')
            except IOError as e:
                continue
        if error1 == 'error1':
            return False
        if error1.startswith('accept1'):
            return True

    def login_check():
        user_name = username.get()
        if ' ' not in user_name:
            if login():
                audience_names = error1[7:]
                match_win(audience_names)
            else:
                messagebox.showinfo(message="Enter other username: ", title='username error')
        else:
            messagebox.showinfo(message='do not use space in your username', title='username error')

    login_frame = ttk.Frame(root, padding=(50, 50, 62, 62))
    login_frame.grid(column=0, row=0)
    name_label = Label(login_frame, text='username: ')
    name_label.grid(column=1, row=1)
    username = StringVar()
    name = Entry(login_frame, width=20, textvariable=username)
    name.grid(column=2, row=1)
    set_name = Button(login_frame, text='set username', command=login_check)
    set_name.grid(column=2, row=2)


login_win()


def match(audiences):
    for audience in audiences:
        server_socket.send(bytes(audience, 'utf-8'))
        error2 = None
        while not error2:
            try:
                while not error2:
                    error2 = server_socket.recv(1024).decode('utf-8')
            except IOError as e:
                pass
            if error2 == 'error2':
                audience = input('{} is offline enter other audience username: '.format(audience))
                server_socket.send(bytes(audience, 'utf-8'))
                error2 = None
            if error2 == 'wait':
                print('please wait')


root.mainloop()
#    time.sleep(5)
