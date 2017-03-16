'''
The MIT License (MIT)
Copyright (c) 2013 Dave P.
'''

import signal
import sys
import ssl
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
from optparse import OptionParser
from PicarioServer import *


# data structures for managing clients
maxPlayers = 16
openIds = []
clients = {}

# setup data structures for managing clients
for i in range(1, maxPlayers + 1):
   openIds.append(i)
   clients[i] = None

def canJoin():
   if not openIds:
       return False
   else:
       return True

def refuseConnection(socket):
   print("Refused Connection")

def acceptConnection(socket):
    thisID = openIds.pop(0)
    clients[thisID] = socket
    socket.myId = thisID
    print("Accepted Connection with id: " + str(thisID))

# handles client socket organization when client disconnects
def disconnect(socket):
   clients[socket.myId] = None
   openIds.append(socket.myId)

# prints out the state of client sockets within server
def debugClients():
   print("Clients  : " + str(clients))
   print("Open Ids : " + str(openIds))


class Socket(WebSocket):

   myId = 0

   def handleMessage(self):
      for client in clients:
         if client != self:
            client.sendMessage(self.address[0] + u' - ' + self.data)

   def handleConnected(self):
      if(canJoin()):
         acceptConnection(self)
      else:
         refuseConnection(self)
      debugClients()

   def handleClose(self):
      disconnect(self)
      debugClients()


if __name__ == "__main__":

   parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
   parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
   parser.add_option("--port", default=8000, type='int', action="store", dest="port", help="port (8000)")
   parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
   parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
   parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")

   (options, args) = parser.parse_args()

   cls = Socket

   if options.ssl == 1:
      server = SimpleSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
   else:
      server = SimpleWebSocketServer(options.host, options.port, cls)

   def close_sig_handler(signal, frame):
      server.close()
      sys.exit()

   signal.signal(signal.SIGINT, close_sig_handler)

   server.serveforever()
