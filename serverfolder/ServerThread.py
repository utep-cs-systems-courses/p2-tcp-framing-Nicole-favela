#! /usr/bin/env python3

# Echo server program

import socket, sys, re, os
sys.path.append("../lib")       # for params
import params
from threading import Thread,Lock
inTransfer  = set()
switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )
buff = b"" #byte buffer 


progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort)) #binds port and address
s.listen(5)              # allow only 5 max connections
# s is a factory for connected sockets
fileExists = False

fullPath = ''
#checking filename initially to see it can be added 
def checkTransfer(filename):
    global inTransfer #global set that makes sure file is not already attempting be transfered from another client
    canTransfer = False
    if filename in inTransfer:
        canTransfer = False
        os.write(1,("file name already in set, cannot modify").encode())
        
    else: #unique filename,add
        canTransfer = True
        inTransfer.add(filename)
    return canTransfer
#for receiving msg and filename
def framedRecv(self):
    state = "getbytes"
    payload = ""
    global buff
    lengthOfMsg = 0
    while 1:
        msg = self.sock.recv(1024) #receives 1 kn of data
        buff+=msg #adds msg to buffer
        if len(msg) ==0: #no msg 
            if len(buff)!=0:
                print("msg incomplete")
            return None
        if state == "getbytes": #separates frame
            
            match = re.match(b'([^:]+):(.*)',buff,re.DOTALL | re.MULTILINE)
            if match:
                strlength, buff = match.groups()
                try: #get int part of frame
                    lengthOfMsg = int(strlength)
                    
                except:
                    os.write(1,("bad msg format").encode())
            state = "getFileData"
        #gets string from frame
        if state == "getFileData":
            
            if len(buff) >= lengthOfMsg:
                payload = buff[0: lengthOfMsg]
                buff = buff[lengthOfMsg:]
        return payload #bytes from frame 
lock = Lock() 
class client1(Thread):
    def __init__(self, sockAddress):
        Thread.__init__(self)
        self.sock, self.addr = sockAddress
        
    def run(self):
        os.write(1,("thread connecting from:..... ").encode())
        host, port = self.addr
        os.write(1,(host).encode())
        os.write(1,("\n").encode())
        while 1:
            lock.acquire() #blocks one thread 
            fileName = framedRecv(self) #gets filename from msg
            os.write(1,("filename: ").encode())
            os.write(1,("\n").encode())
            os.write(1,fileName)
            if checkTransfer(fileName): #if file is able to be transferred meaning it was not already in set()
                lock.release()#makes resource available to another thread 
        
                path = os.getcwd() #gets path of current directory 
                filePath = path+'/'+fileName.decode() #getting full path for filename
            
                if os.path.exists(fileName.decode()): #remove old file 
                    os.remove(fileName.decode())
                if os.path.isfile(filePath):
                    os.write(1,("file already exists").encode())
                    self.sock.send("file exists".encode())
                    sys.exit(0)
                self.sock.send("preparing to write to file".encode())
                f = open(fileName.decode(),'wb')
                #open and write file
                os.write(1,("writing to file....... ").encode())
                fileData = framedRecv(self)
                f.write(fileData)#writes file 
            self.sock.close()#closes socket
            return
            
while True:
    conn = s.accept() # wait until incoming connection request (and accept it)
    server = client1(conn)
    server.start()#starts thread
   
