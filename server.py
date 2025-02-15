import socket
import sys
import IRC_Protocol as irc
from _thread import *

# Global Variables
username_list = []  # list to hold users
chatroom_list = []  # list to hold rooms
pm_list = []  # list to hold pms
quit = 0
host = "localhost"
port = 8080
count = 0

###########################################################
# Function Declarations
###########################################################


def initialize(conn, data):  # Function that adds client connection as a user to the server. Takes as argument a socket obj and a protocol obj
    # global count
    name = data['msg']
    # create user object, which is a dictionary
    user = {'conn': conn, 'name': name, 'msgct': 0}

    username_list.append(user)  # add user to userlist

    print(f"Connected to {conn}, who goes by {name}")

    # get index of the user from the username list to use as user ID
    ul_index = username_list.index(user)
    user['id'] = ul_index  # id key-value added

    print(f"Assigned id number {ul_index} to {name}")

    welcome = f"Welcome {data['msg']}"
    # length = len(welcome)

    # Send a welcome message to user as confirmation with OP Code 101
    # user['msgct'] = user['msgct'] + 1
    # print(f"Count: {count} sent to {name}")
    response = irc.pack(101, ul_index, None, None, 0, welcome)
    result = irc.send(conn, response)

    if 'failed' in result:  # socket fail check
        leave(conn, user)

    print(result)

    return user


# Function that creates a room. Takes as arg socket obj, protocol obj, user obj
def create_room(conn, user):
    # global count
    ul_index = user['id']  # get id of the user

    rm_members = [user]  # create memberlist
    # user['msgct'] = user['msgct'] + 1
    if len(chatroom_list) == 0:  # room list empty, create first room

        room = {'num': 0, 'userlist': rm_members}  # create room obj
        # add room and room member list to chatroom list
        chatroom_list.append(room)
        username = user['name']
        room_created = f"Room 0 was created. \n{username} entered Room 0 \n"

        file_op('room0', room_created)  # Keep history

        # Send a room creation and entry message to user as confirmation with Op Code 201
        # user['msgct'] = user['msgct'] + 1 counted twice
        # print(f"Count: {count} sent to {username}")
        response = irc.pack(201, ul_index, None, 0,
                            0, room_created)
        result = irc.send(conn, response)

        if 'failed' in result:  # socket fail check
            leave(conn, user)

        print(result)

    else:  # rooms exist
        room_num = len(chatroom_list)
        name_room = f"room" + str(room_num)
        room = {'num': room_num, 'userlist': rm_members}  # create room obj

        # add room and room member list to chatroom list
        chatroom_list.append(room)
        room_created = f"Room {room_num} was created.\n{user['name']} entered Room {room_num} \n"

        file_op(name_room, room_created)  # Keep history

        # Send a room creation and entry message to user as confirmation with Op Code 201
        # user['msgct'] = user['msgct'] + 1
        # print(f"Count: {count} sent to {user['name']}")
        response = irc.pack(201, ul_index, None, room_num,
                            0, room_created)
        result = irc.send(conn, response)

        if 'failed' in result:  # socket fail check
            leave(conn, user)

        print(result)


def display_room():  # Function that displays room list.
    room_length = len(chatroom_list)
    room_disp = f'List of Rooms: \n'
    if room_length != 0:
        for room in chatroom_list:
            rm_index = room['num']
            room_disp = room_disp + f'Room #[{rm_index}]'

        return room_disp

    else:
        return 'There are no rooms to join. Please create one.'


# Function that displays a userlist in a room. Takes protocol obj and user obj
def display_rmusers(data, user):
    room_num = int(data['roomid'])
    ulist = f'Users in Room {room_num}: \n'
    room_length = len(chatroom_list)

    # copy list of users to a string
    if room_length > 0 and room_num < room_length:
        room = chatroom_list[room_num]
        for user in room['userlist']:
            id = user['id']
            ulist = ulist + f'[{id}]' + user['name'] + ' '
        ulist = ulist + '\n'
        return ulist
    else:
        return "ERROR: room doesn't exist"


def display_users():  # Function that displays all users
    ulist = f'User List: \n'
    total = len(username_list)

    # copy list of users to a string
    if total > 0:
        for user in username_list:
            id = user['id']
            ulist = ulist + f'[{id}] ' + user['name'] + ' '
        ulist = ulist + '\n'
        return ulist
    else:
        return "ERROR: No users available"


def join_room(conn, user):  # Function that joins a user into a room
    # global count
    ul_index = user['id']
    name = user['name']

    # Display rooms for user to choose from
    returned = display_room()

    if 'create' in returned:
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(251, ul_index, None, None, 0, returned)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
            print(f"Count: {count} sent to {name}")
    else:
        room_disp = f'Please enter the desired room number to join: \n {returned}'
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(251, ul_index, None, None,
                            0, room_disp)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)

    print(result)

    print('Asking client for the desired room number...')

    chosen = irc.received(conn)
    # user['msgct'] = chosen['msgct']
    if chosen['code'] == 250:  # User sent back a room number
        print(f"Adding {name} to a room...")  # Internal message
        rm_requested = int(chosen['roomid'])
        room_length = len(chatroom_list)

        # room list empty, or requested room does not exist
        if room_length == 0 or rm_requested >= room_length or rm_requested < 0:
            no_room = f"No Room {rm_requested} exits"
            # Send error message that such room does not exist.
            # user['msgct'] = user['msgct'] + 1
            response = irc.pack(214, ul_index, None,
                                0, 0, no_room)
            result = irc.send(conn, response)
            # print(f"Sent ccount {count}")
            if 'failed' in result:  # socket fail check
                leave(conn, user)

            print(result)

            print('No such room exists')

        else:  # room requested exists
            joined = f"{name} entered Room {rm_requested} \n"
            rm_name = f'room' + str(rm_requested)

            file_op(rm_name, joined)  # Keep history

            room = chatroom_list[rm_requested]
            # adduser = {'conn': conn, 'name': name, 'msgct': 0,
            # 'id': ul_index}  # create user obj

            for u in room['userlist']:
                # Send a user joined message with Op Code 211
                response = irc.pack(211, user['id'], None,
                                    rm_requested, 1, joined)
                result = irc.send(u['conn'], response)
                # print(f"Sent ccount {count} for {user}")
                if 'failed' in result:  # socket fail check
                    leave(conn, user)
                print(result)

            room['userlist'].append(user)  # add user to room's userlist

            response = irc.pack(211, user['id'], None,
                                rm_requested, 0, joined)
            result = irc.send(conn, response)
    else:
        error = "User failed to send back a room number"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(254, ul_index, None, None,
                            0, error)
        result = irc.send(conn, response)
        # print(f"Sent ccount {count}")
        if 'failed' in result:  # socket fail check
            leave(conn, user)
        print(result)


def post_msg(data, user):  # Function that posts user message in a room with Op Code 211. Takes protocol obj and user obj as argument
    # global count
    name = user['name']
    room_num = data['roomid']
    chat = f"{name}: {data['msg']} \n"
    room = chatroom_list[room_num]
    fname = f'room' + str(room_num)

    file_op(fname, chat)  # Keep history

    # Post message to chat room with username appended with Op Code 221
    for u in room['userlist']:
        if u['conn'] == user['conn']:
            print(f"Found matching user")
            response = irc.pack(221, user['id'], None,
                                room_num, 0, chat)
            result = irc.send(u['conn'], response)
        else:
            response = irc.pack(221, user['id'], None,
                                room_num, 1, chat)
            result = irc.send(u['conn'], response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
        print(result)


def multi_join(conn, data, user):  # Function that allows adding users to multiple rooms with Op Code 701, takes socket obj, protocol obj, and user obj as arg
    global count
    desired = int(data['msg'])
    print(desired)
    print(len(chatroom_list))
    # Valid input check
    if desired > len(chatroom_list):
        failed = "Too many rooms selected"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(704, user['id'], None, None, 0, failed)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
    else:
        msg = "Good to ask to send individual join requests"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(701, user['id'], None, None, 0, msg)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)


def multi_msg(conn, data, user):  # Function that allows sending message to multiple rooms with Op Code 721. Takes as arg socket obj, protcol obj, and user obj
    global count
    desired = int(data['msg'])

    # Valid input check
    if len(chatroom_list) < desired:
        failed = "Too many rooms selected"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(724, user['id'], None, None, 0, failed)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
    else:
        msg = "Good to ask to send individual msg requests"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(721, user['id'], None, None, 0, msg)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)


# Function that posts message to PM. Takes as arg socket obj, protocol obj, and user obj
def post_pm_msg(uconn, data, user):
    global count
    name = user['name']
    rcvrid = data['rcvrid']
    chatid = data['roomid']
    pm = pm_list[chatid]
    conn_list = []
    msgct_list = []
    chat = f"{name}: {data['msg']}"
    fname = f'pm' + f'{chatid}'

    # Get user and receiver sockets
    if user['conn'] == pm['user1']['conn']:
        conn_list.append(user['conn'])
        msgct_list.append(0)
        conn_list.append(pm['user2']['conn'])
        msgct_list.append(1)
    else:
        conn_list.append(pm['user1']['conn'])
        msgct_list.append(1)
        conn_list.append(user['conn'])
        msgct_list.append(0)

    if len(conn_list) > 0:
        # Post message to private message with username appended with Op Code 321
        for conn in conn_list:
            index = conn_list.index(conn)
            response = irc.pack(
                321, user['id'], rcvrid, chatid, msgct_list[index], chat)
            result = irc.send(conn, response)
            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)

        file_op(fname, chat)  # Keep history
    else:
        failed = "No user to send PM to"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(324, user['id'], rcvrid,
                            chatid, 0, failed)
        result = irc.send(uconn, response)
        if 'failed' in result:  # socket fail check
            leave(uconn, user)
        print(result)


def leave_room(conn, data, user):  # Function that removes user from a room
    global count
    room_num = int(data['roomid'])
    name = user['name']
    leaving = f"{name} left the room"
    length = len(chatroom_list)

    # valid room number check
    if room_num < length and room_num >= 0:
        room = chatroom_list[room_num]
        fname = f'room' + str(room_num)

        file_op(fname, leaving)  # Keep history

        if user in room['userlist']:
            room['userlist'].remove(user)  # remove user from the userlist
            print(f"{name} removed\n")
            # user['msgct'] = user['msgct'] + 1
            response = irc.pack(241, user['id'], None, room_num,
                                0, leaving)
            result = irc.send(conn, response)

            # Send message to removed user

            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)

            # Send remaining users on the room's userlist a message
            for u in room['userlist']:
                response = irc.pack(241, user['id'], None, room_num,
                                    1, leaving)
                irc.send(u['conn'], response)
                if 'failed' in result:  # socket fail check
                    leave(conn, user)
                print(result)
        else:
            leaving = f"{name} not in userlist\n"
            # user['msgct'] = user['msgct'] + 1
            response = irc.pack(244, user['id'], None, room_num,
                                0, leaving)
            # Send message to removed user
            result = irc.send(conn, response)
            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)

    else:
        fail = "Failed to find the room on the list to remove\n"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(244, user['id'], None, room_num,
                            0, fail)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
        print(result)
        print("Failed to find the room on the list to remove\n")


# Function that removes user from a pm. Takes as arg socket obj, protocol obj, user obj
def leave_pm(conn, data, user):
    global count
    room_num = data['roomid']
    rcvrid = data['rcvrid']
    name = user['name']
    leaving = f"{name} left"
    length = len(pm_list)

    # Valid room number check
    if room_num < length and room_num > 0:
        pm = pm_list[room_num]
        fname = f"pm" + f"{room_num}"

        file_op(fname, leaving)  # Keep history

        # Send each client on the room's userlist a message that client left the room with Op Code 341
        if pm['user1']['msgct'] == user['msgct']:
            pm['user1']['msgct'] = 0
            pm['user2']['msgct'] = 1
        else:
            pm['user1']['msgct'] = 1
            pm['user2']['msgct'] = 0

        response = irc.pack(341, user['id'], rcvrid, room_num,
                            pm['user1']['msgct'], leaving)
        result = irc.send(pm['user1']['conn'], response)
        response = irc.pack(341, user['id'], rcvrid, room_num,
                            pm['user2']['msgct'], leaving)
        result = irc.send(pm['user2']['conn'], response)

        if 'failed' in result:  # socket fail check
            leave(conn, user)
        print(result)

    else:
        fail = "Failed to find the pm on the list"
        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(344, user['id'], None, room_num,
                            0, fail)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
        print(result)
        print("Failed to find the room on the list to remove\n")


def leave(conn, user):  # Function for processing user request to leave server
    global count
    print('in leave function')
    if len(pm_list) > 0:  # private messages exist
        for pm in pm_list:
            index = pm_list.index(pm)
            fname = f"pm" + f"{index}"
            if pm['user1'] == user or pm['user2'] == user:  # pms exists for user
                pm_list.remove(pm)  # remove pm

    if len(chatroom_list) > 0:  # chatrooms exist
        for room in chatroom_list:  # User in rooms
            if user in room['userlist']:
                room['userlist'].remove(user)  # remove user from userlist

    # remove user from username list
    username_list.remove(user)
    bye = "Goodbye!"
    # Send user disconnect message with Op Code 401
    # user['msgct'] = user['msgct'] + 1
    response = irc.pack(401, None, None,
                        None, 0, bye)
    result = irc.send(conn, response)
    if 'failed' in result:  # socket fail check
        leave(conn, user)
    print(result)
    conn.close()
    print('Successfully disconnected client\n')


def initiate_pm(conn, data, user):  # Function for setting up PM message
    global count
    name = user['name']
    if data['rcvrid'] != None:  # Remember rcvrid is in str
        rcvrname = data['rcvrid']

        for user in username_list:
            if user['name'] == rcvrname:  # found receiver
                rcvr = user
        pm_index = -1

        if len(pm_list) > 0:  # private messages exist
            for pm in pm_list:
                if pm['user1'] == rcvr and pm['user2'] == user:  # pm exists between the two
                    pm_index = pm['num']
                elif pm['user1'] == user and pm['user2'] == rcvr:  # pm exists between the two
                    pm_index = pm['num']

            if pm_index != -1:  # found pm between the two
                # read the pm history
                pm = f"pm{pm_index}"
                pfile = open(f"{pm}.txt", 'a+')
                history = pfile.read()
                # Send client the entire private message history between the users with Op Code 301
                # user['msgct'] = user['msgct'] + 1
                response = irc.pack(301, user['id'], rcvr['id'], pm_index,
                                    0, history)
                result = irc.sendall(conn, response)
                if 'failed' in result:  # socket fail check
                    leave(conn, user)
                print(result)

        else:  # pm between the two not found, start one
            length = len(pm_list)
            pm = {'num': length, 'user1': user, 'user2': rcvr}
            pm_list.append(pm)  # add to pm list
            # create and open new file
            pfile = open(f"pm{length}.txt", 'a+')
            pm_created = f"Private Messaging between {name} and {rcvrname} started\n"
            pfile.write(pm_created)  # Keep history
            pfile.close()
            # Send a pm creation and start message to user as confirmation with Op Code 301
            # user['msgct'] = user['msgct'] + 1
            response = irc.pack(301, user['id'], rcvr['id'], length,
                                user['msgct'], pm_created)
            result = irc.send(conn, response)
            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)
            print('Successfully started PM\n')
    else:
        error = "ERROR: Cannot initiate PM"
        print(error)

        # user['msgct'] = user['msgct'] + 1
        response = irc.pack(304, user['id'], None, None,
                            0, error)
        result = irc.send(conn, response)
        if 'failed' in result:  # socket fail check
            leave(conn, user)
        print(result)


def file_op(file_name, msg):  # Function to deal with files, takes as arg str and str
    try:
        file = open(f"{file_name}.txt", 'a+')
        print("File opened")
    except:
        print("File operation failed at open\n")

    try:
        file.write(msg)  # record in history
        print("Wrote to file")
    except:
        print("File operation failed at writing\n")

    try:
        file.close()
        print("Closed file")
    except:
        print("File operation failed at close\n")


def operations(conn):  # Function that runs the server
    global count
    counter = 0
    while (counter != 1):  # Loop to keep server open until operations done

        data = irc.received(conn)  # Wait for client requests

        # print(f'Data received: {data}') # DEBUG

        if data == None:
            leave(conn, user)

        # index = data['sndrid']
        # grab user, username, and userid if available
        if len(username_list) > 0:
            for u in username_list:
                if u['conn'] == conn:
                    print("In loop to get user info and cnt")
                    name = u['name']
                    ul_index = u['id']
                    user = u
                    # user['msgct'] = data['msgct']
                    # print(f"Count: {count} for {name}")

 #       if index != None:
 #           if index < len(username_list) and index >= 0:
 #               name = username_list[index]['name']
 #               ul_index = index
 #               user = username_list[index]

        # OP Code 100: Client connected and wants to register a username
        if data['code'] == 100:
            user = initialize(conn, data)

        # Op Code 200: User requested to create a room
        elif data['code'] == 200:
            print(f"Creating a room for {name}...\n")
            create_room(conn, user)

        # Op Code 210: User requests to join a room
        elif data['code'] == 210:
            print('Displaying room list for client...\n')
            join_room(conn, user)

        # Op Code 220: User is messaging a room
        elif data['code'] == 220:
            print(f'{name} wants to message...\n')
            post_msg(data, user)

        # Op Code 230: User wants display of userlist in a room
        elif data['code'] == 230:
            room_num = data['roomid']

            print(f'{name} wants to see the list of users in the room...\n')
            ulist = display_rmusers(data, user)
            if 'ERROR' in ulist:
                print(ulist)

            # Send client the list of users in the chat room with Op Code 231
            # user['msgct'] = user['msgct'] + 1
            response = irc.pack(231, ul_index, None, room_num,
                                0, ulist)
            result = irc.send(conn, response)
            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)

        # Op Code 240: User requested to leave a room
        elif data['code'] == 240:
            print(f'{name} wants to leave the room...\n')
            leave_room(conn, data, user)

        # Op Code 260: User requested to see roomlist
        elif data['code'] == 260:
            # internal message
            print(f'{name} wants to see list of rooms...\n')
            returned = display_room()
            if 'create' in returned:
                print("Room list empty\n")

            # user['msgct'] = user['msgct'] + 1
            response = irc.pack(251, ul_index, None, None,
                                0, returned)
            result = irc.send(conn, response)
            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)

        # Op code 300: User requested to initiate private message a user
        elif data['code'] == 300:
            print(f'{name} wants to PM someone...\n')
            initiate_pm(conn, data, user)

        # Op Code 320: User is private messaging
        elif data['code'] == 320:
            print(f'{name} wants to message...\n')
            post_pm_msg(conn, data, user)

        # Op Code 330: User wants display of all users
        elif data['code'] == 330:
            print(f'{name} wants to see the list of all users...\n')
            returned = display_users()
            if 'ERROR' in returned:
                print("User list empty\n")
            # user['msgct'] = user['msgct'] + 1
            print(f"Count: {count} sent")
            response = irc.pack(331, ul_index, None, None,
                                0, returned)
            result = irc.send(conn, response)
            if 'failed' in result:  # socket fail check
                leave(conn, user)
            print(result)

        # Op Code 340: User requested to leave private message
        elif data['code'] == 340:
            # internal message
            print(f'{name} wants to leave the private message...\n')
            leave_pm(conn, data, user)

        # Op Code 400: User requested to disconnect
        elif data['code'] == 400:
            print(f'{name} wants to close connection...\n')  # internal message
            leave(conn, user)
            counter = 1
            break

        # Op Code 405: Nothing in input stream
        elif data['code'] == 405:
            print("Nothing in input stream... \n")

        # Op Code 700: User requested to join multiple rooms
        elif data['code'] == 700:
            print(f'{name} wants to join multiple rooms...\n')
            multi_join(conn, data, user)

        # Op Code 720: User requested to message multiple rooms
        elif data['code'] == 720:
            print(f"{name} wants to message multiple rooms...\n")
            multi_msg(conn, data, user)

        else:
            code = data['code']
            print(
                f"Something went wrong. Received code {code}. Connecting to client failed. Closing server... \n")
            for user in username_list:
                print(f"User: {user}")
                leave(user['conn'], user)
            counter = 1
            global quit
            quit = 0


###########################################################
# CODE START
###########################################################
# server start
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Using IPv4 and TCP

try:
    s.bind((host, port))  # server socket set up
except socket.error as error:
    print(f"An error occured: {str(error)} \n")

print('Server is up and waiting...\n')
s.listen()  # wait for client socket to connect

while quit != 1:
    conn, addr = s.accept()  # accept socket connection
    start_new_thread(operations, (conn,))

print("Ending program. Bye! \n")
sys.exit()
