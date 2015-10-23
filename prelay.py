#!/usr/bin/python3

import socket,select,sys,argparse

socklist = []           #List of client sockets
relay_sock = {}         #Dict of sckets with connecting port
s = select.select

#Accepts the connection from the client and connects back to the client on the originating port
def xaccept(s, host, port):
	sock, addr = s.accept()
	relay = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:   #Try connecting remote host
		relay.connect((host, int(port)))
	except:
		return
	if relay:   # If the connection was successful save the connection info in to a lit and dict       
		socklist.append(sock)
		socklist.append(relay)
		relay_sock[sock] = relay
		relay_sock[relay] = sock
	else:          
		clientsock.close()

#send data through the relay
def xrecv(data,s):
	relay_sock[s].send(data)	   #Sends the data	

#closes the connecion
def xclose(s):
	discon = s.getpeername()
	#print(bcolors.RED+'[-]'+bcolors.ENDC+'Disconnected from %s:%s' % (discon[0],discon[1]))
	fin = relay_sock[s]
	socklist.remove(s)
	socklist.remove(fin)
	relay_sock[fin].close()               #closes the connection of one part of relay
	fin.close()                     #closes the connection of the other part of the relay
	del relay_sock[fin]
	del fin

#argument Parser
arg = argparse.ArgumentParser()
arg.add_argument("-c", dest = "lport", help="Local Host Port    ", default="x")
arg.add_argument("-l", dest = "lhost", help="Local Host IP      ", default="x")
arg.add_argument("-m", dest = "rport", help="Remote Host Port   ", default="x")
arg.add_argument("-r", dest = "rhost", help="Remote Host IP     ", default="x")
args = arg.parse_args()

#If no ports the print usage
if len(sys.argv) == 8 or args.lport == "x" or args.rport == "x" or args.lhost == "x" or args.rhost == "x":
	print("Usage python3 prelay.py -c 4444 -l 192.168.1.2 -m 445 -r 192.168.3.2")
	exit()
#For each port in arg, open a listening socket
try:
	lhost = socket.socket()                       
	lhost.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	lhost.bind(('', int(args.lport)))       
	lhost.listen(5)            
	socklist.append(lhost)
except:
	print("Port %s is in use, try again using another port" % args.lport)
	exit()
while True:
	rlist, wlist, xlist = s(socklist, [], [])
	for i in rlist:
		if i == lhost:
			xaccept(i,args.rhost,args.rport)
			break
		try:   #If received data send on through the relay in not close
			data = i.recv(4096)
			if len(data) == 0:
				xclose(i)
			else:
				xrecv(data,i) 
		except:
			pass