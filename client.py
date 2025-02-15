# client
import socket
import IRC_Protocol as irc
import os
import sys
import time

HOST = "localhost"
PORT = 8080

# Global Variables
main_op = 'Please choose: [1] Display Users  [2] Create a Room  [3] Join a Room  [4] Join Multiple Rooms [5] Display list of Rooms [6] Private Message [0] Quit Program \n'
room_op = 'You can type words to chat. Please type [1] to Display Users in the room or [0] to Leave the room \n'
pm_op = 'You can type words to chat. Please type [0] to Leave private message \n'
loop = 1
in_room = False
in_pm = False
room_num = -1
repeat = 1
multi = False
room_list = []
count = 0

###########################################################
# Function Declaration
###########################################################


def file_op(file_name, msg):  # Function that writes in files. Takes str and str as args
    try:
        file = open(f"client{file_name}.txt", 'a+')
    except:
        print("File operation failed at open\n")

    try:
        file.write(msg)  # record in history
    except:
        print("File operation failed at writing\n")
    try:
        file.close()
    except:
        print("File operation failed at close\n")


def show_chat(file_name):  # Function that shows entire chat history on screen. Takes str as arg
    try:
        file = open(f"client{file_name}.txt", 'r')
    except:
        print("File operation failed at open\n")
    try:
        history = file.read()  # read history
        print(history)
    except:
        print("File operation failed at reading\n")


def update(s, fname, data):  # Function to handle updates to chat. Takes socket obj and protocol obj as args
    global in_room
    global in_pm
    global loop
    global count

    count = data['msgct']

    if in_room == True or in_pm == True:
        while count > 0:
            print("In update loop...")
            if data['code'] == 211:
                print("in 211")
                room_num = int(data['roomid'])  # Save room number
                if multi == False:  # Only current room is open
                    os.system('cls')

                fname = f'Room{room_num}'

                file_op(fname, data['msg'])  # Keep history on client side

                print(f"{data['msg']}")  # Option 1: Print message to screen
            # show_chat(fname) # Option 2: Show entire updated history
            elif data['code'] == 221:
                file_op(fname, data['msg'])  # Keep history on client side
                print(f"{data['msg']}")
            elif data['code'] == 231:  # in a room # Displaying Userlist in a room is Successful
                print("in 231")
                # if data['msg'] != old['msg']:
                print(f"{data['msg']}")  # Option 1: Print to screen
                # os.system('cls') # Option 2: Clear screen
            # show_chat(fname) # Option 2: Show entire updated history
            elif data['code'] == 241:
                print("in 241")
                print(f"{data['msg']}")  # Keep history on client side
            elif data['code'] == 321:  # in pm
                print("in 321")
                print(f"{data['msg']}")
            elif data['code'] == 341:
                print("in 341")
                print(f"{data['msg']}")  # Keep history on client side
            else:
                print("in else")
                code = data['code']
                roomid = data['roomid']
                print(
                    f'Server encountered an error while posting a message in room {roomid} code {code}. Disconnecting from the server...\n')
                loop = 0
                close_socket(s, my_id)

            data = irc.received(s)
            count = data['msgct']

        count = 0
    return data


# Function to handle error by closing socket. Takes socket obj and int as args
def close_socket(s, my_id):
    global loop
    global count

    disconnect = irc.pack(400, my_id, None, None, count, None)
    # Message server client will disconnect
    result = irc.send(s, disconnect)

    # Receive reply from server but we don't really care
    data = irc.received(s)

    loop = 0

    try:
        s.close()
        print("Successfully disconnected. Goodbye! \n")
    except:
        print("Ending program. Goodbye! \n")
        sys.exit()


def display_room(s, my_id):  # Function to display rooms. Takes socket obj and int as args
    global loop
    global count
    # global count
    # count = count + 1
    # print(f'Count: {count} sent')
    display = irc.pack(260, my_id, None, None, 0, None)
    result = irc.send(s, display)  # Message server to display rooms

    if 'failed' in result:  # socket fail check
        print("ERROR: Socket disconnected...closing application \n")
        sys.exit()

    data = irc.received(s)   # Receive reply from server

    count = data['msgct']

    if count > 0:
        data = update(s, fname, data)

    if data['code'] == 251:
        print(f"{data['msg']}")
    elif data['code'] == 254:
        print("Error choosing a room \n")
    elif data['code'] == 264:
        print("Error displaying room \n")
    else:
        code = data['code']
        print(
            f'Server encountered an error displaying rooms with code {code}. Disconnecting from the server...\n')
        loop = 0
        close_socket(s, my_id)


def join_room(s, my_id, roomid):  # Function to join a room. Takes socket obj, int, and int as args
    global loop
    global room_num
    global multi
    global in_room
    global count
    # global count
    # count = count + 1
    # print(f'Count: {count} sent')
    chosen = irc.pack(250, my_id, None, roomid, 0, None)
    # Message server the choosen room number
    result = irc.send(s, chosen)
    if 'failed' in result:  # socket fail check
        print("ERROR: Socket disconnected...closing application \n")
        sys.exit()

    data = irc.received(s)   # Receive reply from server

    # Room successfully joined. User now in room.
    if data['code'] == 211:
        room_num = int(data['roomid'])  # Save room number
        if multi == False:  # Only current room is open
            os.system('cls')

        in_room = True
        fname = f'Room{room_num}'

        file_op(fname, data['msg'])  # Keep history on client side

        print(room_op)
        print(f"{data['msg']}")  # Option 1: Print message to screen
        # show_chat(fname) # Option 2: Show entire updated history
    if data['code'] == 214:
        print(f"{data['msg']}")
    else:
        code = data['code']
        print(
            f'Server encountered an error joing a room with code {code}. Disconnecting from the server...\n')
        loop = 0
        close_socket(s, my_id)


# Function for posting messages to a room. Takes socket obj, int, int as args.
def msg_room(s, my_id, roomid):
    global loop
    global count
    # global count
    fname = f'Room{roomid}'
    # count = count + 1
    # print(f'Count: {count} sent')

    chat = irc.pack(220, my_id, None, roomid,
                    0, choice)
    # Message server to post chat message
    result = irc.send(s, chat)
    if 'failed' in result:  # socket fail check
        print("ERROR: Socket disconnected...closing application \n")
        sys.exit()

    data = irc.received(s)
    roomid = data["roomid"]
    fname = f"Room{roomid}"
    count = data['msgct']

    if count > 0:
        data = update(s, fname, data)

    if data['code'] == 221:
        file_op(fname, data['msg'])  # Keep history on client side
        print(f"{data['msg']}")  # Option 1: Print to screen
        # os.system('cls') # Option 2: Clear screen
        # show_chat(fname) # Option 2: Show entire updated history
    else:
        code = data['code']
        print(
            f'Server encountered an error while posting a message in room {roomid} code {code}. Disconnecting from the server...\n')
        loop = 0
        close_socket(s, my_id)


###########################################################
# CODE START
###########################################################
# Create socket to connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((HOST, PORT))  # connect to socket

# Initialize with Op Code 100
print("Please enter your username: ")
name = input()

initial = irc.pack(100, None, None, None, 0, name)
result = irc.send(s, initial)  # Send username to server as initial message

if 'failed' in result:  # socket fail check
    print("ERROR: Socket disconnected...closing application \n")
    sys.exit()

data = irc.received(s)   # Receive reply from server

if data['code'] == 101:  # Server successfully initialized
    my_id = data['sndrid']  # keep track of user id
    # print(f"{data}")  # debug
    print(f"{data['msg']}")
else:
    print(f'Server encountered an error 1. Disconnecting from the server...\n')
    loop = 0
    close_socket(s)

# Loop for server messages or client input
while loop == 1:

    if in_room == False and in_pm == False:  # In Main menu
        print(main_op)  # display main options

    choice = input()
    sys.stdout.flush()
    time.sleep(1)

    # Main menu. User wants to disconnect. Op code 400
    if choice == '0' and in_room == False and in_pm == False:
        close_socket(s, my_id)

    # Room Menu. Leave room. Op code 240.
    elif choice == '0' and in_room == True and in_pm == False:

        leave = irc.pack(240, my_id, None, room_num, count, None)
        # Message server to leave room
        result = irc.send(s, leave)
        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)
        roomid = data["roomid"]
        fname = f"Room{roomid}"
        if count > 0:
            data = update(s, fname, data)

        fname = f"Room{data['roomid']}"

        if data['code'] == 241:  # Server can sucessfully remove user from the room
            print(f"{data['msg']}")
            if multi == False:
                in_room = False
                os.system('cls')
            else:
                room_list.remove(room_num)
                if len(room_list) == 0:
                    multi = False
                    in_room = False
        else:
            code = data['code']
            print(
                f'Server encountered an error while leaving room {room_num} with code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    # PM menu. Client wants to leave the PM mode. Op Code 340
    elif choice == '0' and in_room == False and in_pm == True:
        # count = count + 1
        # print(f'Count: {count} sent')
        leave = irc.pack(340, my_id, receiverid,
                         file_index, 0, None)
        # Message server to leave PM
        result = irc.send(s, leave)

        if 'fail' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)   # Receive reply from server
        roomid = data["roomid"]
        fname = f"Room{roomid}"
        count = data['msgct']

        if count > 0:
            data = update(s, fname, data)

        if data['code'] == 341:  # Server can sucessfully remove user from the PM mode
            print(f"{data['msg']}")
            os.system('cls')
            in_pm = False

        else:
            print(f'Server encountered an error 11. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    elif choice == '1' and in_room == True and in_pm == False:  # Room menu. Display Users. Op Code 230

        display = irc.pack(230, my_id, None, room_num, 0, None)
        # Message server to display users
        result = irc.send(s, display)

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        # Receive reply from server
        data = irc.received(s)

        count = data['msgct']

        if count > 0:
            data = update(s, fname, data)

        if data['code'] == 231:  # Displaying Userlist in a room is Successful
            print(f"{data['msg']}")
        else:
            code = data['code']
            print(
                f'Server encountered an error displaying users in room {room_num} with code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    elif choice == '1' and in_room == False and in_pm == False:  # Main menu. Display Users. Op Code 330

        display = irc.pack(330, my_id, None, None, 0, None)

        result = irc.send(s, display)  # Message server to display users

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)   # Receive reply from server

        print(f"Count: {count} updated")

        if data['code'] == 331:  # Displaying Userlist is Successful
            print(f"{data['msg']}")
        else:
            print(
                f'Server encountered an error displaying users. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    # Main menu. Create a room. Op Code 200.
    elif choice == '2' and in_room == False and in_pm == False:

        create = irc.pack(200, my_id, None, None, 0, None)
        result = irc.send(s, create)  # Message server to display users

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)  # Receive reply from server

        if data['code'] == 201:  # Room successfully created. User now in room.
            room_num = data['roomid']  # Save room number
            fname = f"Room{room_num}"
            if multi == False:
                os.system('cls')
            in_room = True
            print(room_op)
            print(f"{data['msg']}")
            file_op(fname, data['msg'])  # Keep history on client side
        else:
            code = data['code']
            print(
                f'Server encountered an error creating a room with code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    elif choice == '3' and in_room == False and in_pm == False:  # Main menu. Join a room. Op Code 210
        # count = count + 1
        # print(f'Count: {count} sent')
        ask = irc.pack(210, my_id, None, None, 0, None)
        # Message server to display the rooms to choose from
        result = irc.send(s, ask)

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)   # Receive reply from server

        print(f'Count: {count} updated')

        if data['code'] == 251:  # Server displayed the chatroom list for user to choose from
            print(f"{data['msg']}")
            room = input()  # User input of room to join
            sys.stdout.flush()
            time.sleep(1)
            join_room(s, my_id, int(room))

        else:
            code = data['code']
            print(
                f'Server encountered an error joining with code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    # Main menu. Wants to join multiple rooms. Op Code 700.
    elif choice == '4' and in_room == False and in_pm == False:

        display_room(s, my_id)

        print("Please enter the rooms you wish to join seperated by comma : \n")
        rooms = [int(rooms) for rooms in input().split(",")]
        # print(rooms)  # DEBUG
        room_list = rooms.copy()
        # print(room_list)
        length = len(room_list)
        # print(length)
        desired = str(length)
        # print(desired)

        ask = irc.pack(700, my_id, None, None, 0, desired)
        # Message server we want to join multiple rooms
        result = irc.send(s, ask)

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)   # Receive reply from server

        print(f'Count: {count} updated')

        if data['code'] == 701:
            for room in room_list:
                join_room(s, my_id, room)
                multi = True
        elif data['code'] == 704:
            print(data['msg'])
        else:
            code = data['code']
            print(
                f'Server encountered an error joining multiple rooms with error code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    # User requests to Display the list of rooms. Op Code 260
    elif choice == '5' and in_room == False and in_pm == False:
        display_room(s, my_id)

    # User requests to Private Message. Op Code  300.
    elif choice == '6' and in_room == False and in_pm == False:
        print("Please enter the username of the user you want to message: \n")
        receiver = input()
        # count = count + 1
        # print(f'Count: {count} sent')
        find = irc.pack(300, my_id, receiver, None, count, None)
        result = irc.send(s, find)  # Message server to find user to PM

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)  # Receive reply from server

        if data['code'] == 301:  # Successfully connected with the receiver to PM
            file_index = data['roomid']
            receiverid = data['rcvrid']  # in str
            fname = f"PM{file_index}"
            file_op(fname, data['msg'])  # Keep history on client side
            os.system('cls')
            print(pm_op)
            print(f"{data['msg']}")  # Option 1: Print to screen
            # show_chat(fname) # Option 2: Show entire updated history
            in_pm = True

        else:
            code = data['code']
            print(
                f'Server encountered an error initiating PM mode with code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    elif in_room == True and in_pm == False and multi == False:  # Room Menu. Send message. Op Code 220
        msg_room(s, my_id, room_num)

    # Room Menu. Send message to multiple rooms. Op code 720
    elif in_room == True and in_pm == False and multi == True:
        end = False
        print("Please enter the rooms you wish to join seperated by comma : \n")
        rooms = [int(rooms) for rooms in input().split(",")]
        print(rooms)
        # Check whether the user is in the rooms user wants to message
        for room in rooms:
            if room not in room_list:
                print("You are not a member of Room {room}!")
                end = True

        if end != True:
            length = len(rooms)
            desired = str(length)

            ask = irc.pack(720, my_id, None, None, 0, desired)
            # Message server we want to message multiple rooms
            result = irc.send(s, ask)

            if 'failed' in result:  # socket fail check
                print("ERROR: Socket disconnected...closing application \n")
                sys.exit()

            data = irc.received(s)   # Receive reply from server

            count = data['msgct']

            if count > 0:
                data = update(s, fname, data)

            if data['code'] == 721:
                for room in room_list:
                    msg_room(s, my_id, room)

            else:
                print(
                    f'Server encountered an error preparing to send messages to multiple rooms. Disconnecting from the server...\n')
                loop = 0
                close_socket(s, my_id)
        else:
            print(
                f'Server encountered an error sending mulitple messages. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    elif in_room == False and in_pm == True and multi == False:  # PM menu. Send message. Op Code 320
        # count = count + 1
        # print(f'Count: {count} sent')
        chat = irc.pack(320, my_id, receiverid,
                        file_index, 0, choice)
        # Message server to post chat message
        result = irc.send(s, chat)

        if 'failed' in result:  # socket fail check
            print("ERROR: Socket disconnected...closing application \n")
            sys.exit()

        data = irc.received(s)

        count = data['msgct']

        if count > 0:
            data = update(s, fname, data)

        count = data['msgct']

        if count > 0:
            data = update(s, fname, data)

        if data['code'] == 221 or data['code'] == 211 or data['code'] == 241 or data['code'] == 321 or data['code'] == 341:
            file_op(fname, data['msg'])  # Keep history on client side
            print(f"{data['msg']}")  # Option 1: Print to screen
            # os.system('cls') # Option 2: Clear screen
            # show_chat(fname) # Option 2: Show entire updated history
        else:
            code = data['code']
            print(
                f'Server encountered an error posting to pm with code {code}. Disconnecting from the server...\n')
            loop = 0
            close_socket(s, my_id)

    else:
        if type(choice) != int:
            print("Non-integer input detected. Please enter a valid integer")
        elif type(choice) == int:
            print("Please input valid integer as your choice")
        else:
            code = data['code']
            print(f"Unknown error encountered with code {code}")

    old_data = data
