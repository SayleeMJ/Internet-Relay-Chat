# File for IRC protocol. Client and server app call on IRC class to wrap data into the protocol
import pickle
import socket


def pack(op_code, sender, receiver, room, count, message):
    protocol = dict(code=op_code, sndrid=sender, rcvrid=receiver,
                    roomid=room, msgct=count, msg=message)
    return protocol


def send(conn, response):
    try:
        conn.send(pickle.dumps(response))
        code = response['code']
        msgct = response['msgct']
        msg = f'Successfully sent message for Op code: {code} and count of {msgct} to {conn}'
    except:
        msg = f"Socket {conn} failed to send"
    return msg


def received(conn):
    try:
        data = pickle.loads(conn.recv(1024))
    except:
        data = pack(405, None, None, None, -1, '')
    return data
