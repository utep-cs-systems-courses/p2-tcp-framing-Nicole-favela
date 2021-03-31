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
    print("in checktransfer")
    global inTransfer #global set that makes sure file is not already attempting be transfered from another client
    canTransfer = False
    if filename in inTransfer:
        canTransfer = False
        os.write(1,("file name already in set, cannot modify").encode())
        
    else: #unique filename,add
        canTransfer = True
        inTransfer.add(filename)
    #release lock
   # lock.release()
    return canTransfer
#for receiving msg and filename
#returns int msg length 
def framedRecv(self):
    state = "getbytes"
    payload = ""
    
    global buff
    lengthOfMsg = 0
    while 1:
        msg = self.sock.recv(1024) #receives 1 kn of data
        #print("msg is: ", msg)
        buff+=msg #adds msg to buffer
        if len(msg) ==0: #no msg 
            if len(buff)!=0:
                print("msg incomplete")
            return None
        print(state)
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
                print("payload: ", payload)
                buff = buff[lengthOfMsg:]
        return payload #bytes from frame 
lock = Lock() 
class client1(Thread):
    def __init__(self, sockAddress):
        Thread.__init__(self)
        self.sock, self.addr = sockAddress
        
    def run(self):
        print("thread1...connecting from: ",self.addr)
        while 1:
            lock.acquire() #blocks one thread 
            fileName = framedRecv(self)
            os.write(1,("filename: ").encode())
            os.write(1,fileName)
            if checkTransfer(fileName):
                lock.release()#makes resource available to another thread
                ##
                path = os.getcwd()
                filePath = path+'/'+fileName.decode()
                print(filePath)
                if os.path.exists(fileName.decode()):
                    os.remove(fileName.decode())
                if os.path.isfile(filePath):
                    print("file already exits")
                    self.sock.send("file exists".encode())
                    sys.exit(0)
                self.sock.send("preparing to write to file".encode())
                f = open(fileName.decode(),'wb')
                
                
                #open and write file 
                print("writing to file......")
                fileData = framedRecv(self)
                f.write(fileData)
                #lock.release()
            self.sock.close()
            return
                
                
                #framed receive and write file
            
while True:
    conn = s.accept() # wait until incoming connection request (and accept it)
    server = client1(conn)
    server.start()
   # if os.fork() == 0:      # child becomes server
    #    if fileExists==False: 
            
           # filePath = os.path.expanduser('~/Documents/TCPfilelab/p2-tcp-framing-Nicole-favela/TCPlab/TransferFiles') #finds directory so it can create the file 
    
           # fileName = conn.recv(1024).decode()
           # os.write(1, fileName.encode()) #
          #  if os.path.exists(filePath):
               # fullPath = os.path.join(filePath,fileName)#accesses text file
               # try:
              #      f = open(fullPath, 'x') #createfile in 
             #       os.write(1, ("file created").encode())
            #        f.close()
             #       fileExists = True
           #         conn.send("ok").encode()
          #      except:
         #           os.write(2, ("file exists already").encode())
            #        fileExists = True
        #    conn.send(b"Ok")
       # framedMsg = conn.recv(1024).decode()
       # print("framed msg", framedMsg)
       # f = open(fullPath, 'w')
       # f.write(framedMsg)#writes contents to framedMsg
       # f.close()
      #  f = open(fullPath,'r') #opens file to read it
     #   print(f.read())
    #    os.write(1,("connected by: ").encode())
   #     os.write(1,addr[0].encode())#prints local host 
  #      conn.shutdown(socket.SHUT_WR)#closes socket connection 

