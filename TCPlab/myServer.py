#! /usr/bin/env python3

# Echo server program

import socket, sys, re, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )



progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort)) #binds port and address
s.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

while True:
    conn, addr = s.accept() # wait until incoming connection request (and accept it)
    if os.fork() == 0:      # child becomes server
        filePath = os.path.expanduser('~/Documents/TCPfilelab/p2-tcp-framing-Nicole-favela/TCPlab/TransferFiles') #change to have path of user inputted 
       # os.write(1,fileName.encode())
        fileName = conn.recv(1024).decode()
        os.write(1, fileName.encode()) #
        if os.path.exists(filePath):
            fullPath = os.path.join(filePath,fileName)
            try:
                f = open(fullPath, 'x') #
                os.write(1, ("file created").encode())
                conn.send("ok").encode()
            except:
                os.write(2, ("file exists already").encode())
                         
        os.write(1,("connected by: ").encode())
        os.write(1,addr[0].encode())
        conn.send(b"hello")
 
        conn.shutdown(socket.SHUT_WR)


