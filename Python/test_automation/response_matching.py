# Version 0.1

import time
import socket
import threading
import datetime

class SA634:
   def __init__(self):
      self.eth_ip = ""
      self.eth_nm = ""
      self.eth_gw = ""
      self.baudrate = ""
      self.serial = ""
      self.datecode = ""
      self.sw_states = [-1, -1, -1, -1]      # current state of switches
      self.last_reply_time_history = []      # running log or replies

   def parse_reply(self, reply):

      matched = False
      reply = reply.upper()
      # (lexi compare)
      if (reply[0:7] == 'SERIAL:'):
         matched = True
         tokens = reply.split(' ')
         self.serial = tokens[1]
         self.datecode = tokens[3]
      elif (reply[0:3] == 'IP:'):
         matched = True
         tokens = reply.split(' ')
         self.eth_ip = tokens[1] 
      elif (reply[0:3] == 'NM:'):
         matched = True
         tokens = reply.split(' ')
         self.eth_nm = tokens[1] 
      elif (reply[0:3] == 'GW:'):
         matched = True
         tokens = reply.split(' ')
         self.eth_gw = tokens[1] 
      elif (reply[0:9] == 'BAUD RATE:'):
         matched = True
         tokens = reply.split(' ')
         self.eth_gw = tokens[3] 
      elif (reply[0:8] == 'SWITCH #'):
         matched = True
         tokens = reply.split(' ')
         self.sw_states[int(tokens[1].strip('#')) -1] = int(tokens[3].strip('J'))

      # historical processing information
      self.last_reply_time_history.append([datetime.datetime.now(), reply, matched])

   def report(self):
      print("System: {0}-{1}".format(self.serial, self.datecode))
      print("Network: IP({0}), NM({1}), GW({2})".format(self.eth_ip, self.eth_nm, self.eth_gw))
      print("Current switch states: [{0}, {1}, {2}, {3}]".format(self.sw_states[0], self.sw_states[1], self.sw_states[2], self.sw_states[3]))
      print("\r\nReply History")
      for evt in self.last_reply_time_history:
         print(evt)

thread_active = True
jfw_779655 = SA634()

# messages from test system
def incoming(session):
    buffer = ''
    while thread_active == True:
        try:
            chunk = session.recv(256)
            if chunk:
                buffer += ''.join(map(chr, chunk))
                last = 0
                process = ''
                for i in range(0, len(buffer)):
                    if buffer[i] == '\n' or buffer[i] == '\r':
                        if (len(process)):
                            # process the response
                            jfw_779655.parse_reply(process)
                            process = ''
                        last = i
                    else:
                        process += buffer[i]
                buffer = buffer[last +1:len(buffer)]
        except BlockingIOError:
            pass
        except ConnectionResetError:
            break
            
# connect to system
session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session.connect(('192.168.1.167', 3001))
session.setblocking(False)

# receive responses and process
t = threading.Thread(target=incoming, args=(session,))
t.start()

session.send(('IDN\n').encode())
session.send(('SS -R 1 2\n').encode()) # set with response example
# .... more command here
session.send(('RAS\n').encode())       # get all switch states updating report before exiting

time.sleep(3)                          # give time for everything to go through
thread_active = False

jfw_779655.report()                    # end of operation report

print('Script done')




