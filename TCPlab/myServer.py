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
fileExists = False

fullPath = ''
while True:
    conn, addr = s.accept() # wait until incoming connection request (and accept it)
    if os.fork() == 0:      # child becomes server
        if fileExists==False: 
            
            filePath = os.path.expanduser('~/Documents/TCPfilelab/p2-tcp-framing-Nicole-favela/TCPlab/TransferFiles') #finds directory so it can create the file 
    
            fileName = conn.recv(1024).decode()
            os.write(1, fileName.encode()) #
            if os.path.exists(filePath):
                fullPath = os.path.join(filePath,fileName)#accesses text file
                try:
                    f = open(fullPath, 'x') #createfile in 
                    os.write(1, ("file created").encode())
                    f.close()
                    fileExists = True
                    conn.send("ok").encode()
                except:
                    os.write(2, ("file exists already").encode())
                    fileExists = True
            conn.send(b"Ok")
        framedMsg = conn.recv(1024).decode()
        print("framed msg", framedMsg)
        f = open(fullPath, 'w')
        f.write(framedMsg)#writes contents to framedMsg
        f.close()
        f = open(fullPath,'r') #opens file to read it
        print(f.read())
        os.write(1,("connected by: ").encode())
        os.write(1,addr[0].encode())#prints local host 
        conn.shutdown(socket.SHUT_WR)#closes socket connection 

