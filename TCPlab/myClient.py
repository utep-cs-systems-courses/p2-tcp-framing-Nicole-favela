#! /usr/bin/env python3

# Echo client program
import socket, sys, re, time,os
sys.path.append("../lib")       # for params
import params
start = 0
max = 0

def frameMsg(socket, payload): #frames msg 
    msg = str(len(payload)).encode()+b':'+ payload.encode()# frames msg by writing out length of msg: msg 
    while len(msg):
        sendMsg = socket.send(msg) #sends msg 
        
def readLine():
    global start
    global max
    line = "" #empty line
    char = getChar()
    while (char != "EOF" and char != ''):
        line+=char #accumulate chars 
        char =getChar()
    start = 0
    max = 0
    return line

def getChar():
    global start
    global max
    
    f = os.open(fileName, os.O_RDONLY) #opens file 
    if start == max:
        start = 0
        max = os.read(f, 10000) #max is the limit of file
        if max == 0:
            return "EOF"
    if start < len(max): #file has contents 
        charArr = chr(max[start]) #creates char array
        start+=1
        os.close(f) #closes file
        return charArr
    else:
        os.close(f) #closes file f
        return "EOF" 
    
switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--delay'), 'delay', "0"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage  = paramMap["server"], paramMap["usage"]

if usage:
    params.usage()

try: 
    serverHost, serverPort = re.split(":", server)#splits by colon
    serverPort = int(serverPort) #changes string to int
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res 
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa)) 
        s.connect(sa) #connects to socket address
        
    except socket.error as msg: 
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

delay = float(paramMap['delay']) # delay before reading (default = 0s)
if delay != 0:
    os.write(1,("sleeping for: \n").encode())#print how long it slept for
    os.write(1,delay.encode())

    time.sleep(delay)

    os.write(1,("done sleeping\n").encode())

fileName = input("input a file name")#gets file from user
if os.path.isfile(fileName):#check if file is in path 
    
    while 1:
        msgName = s.send(fileName.encode()) #sends 
        data = s.recv(1024).decode() #bytes to string object 
        os.write(1, ("received '%s'\n" %data).encode())
        #fileContents = readLine()
        #frameMsg = (s, fileContents) #creates framed msg
        if len(data) == 0:
            break
    os.write(1, ("zero length read: Closing\n").encode())
    s.close()
