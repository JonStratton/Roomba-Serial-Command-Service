#!/usr/bin/env python
__author__ = 'Jon Stratton'
import sys, socket, serial
from zeroconf import ServiceInfo, Zeroconf

# Roomba device settings
serial_dev = '/dev/ttyUSB0'

# Roomba commands to char
roomba_commands = {
   'clean': [128, 131, 135],
   'spot' : [128, 131, 134],
#   'dock' : [128, 131, 143],
   'off'  : [128, 131, 133],
}

# Generic service settings
service_port = 10000
service_addr = ''

# Zeroconf Service settings
service_zc_desc = {'service': 'Roomba Serial Command Service', 'version': '0.1'}
service_zc_info = ServiceInfo("_custom._tcp.local.",
                   'Roomba Serial Command Service._custom._tcp.local.',
                   socket.inet_aton('127.0.0.1'), service_port, 0, 0, service_zc_desc)
zeroconf = Zeroconf()

def roomba_do( command_list ):
   success = 0
   try:
      ser = serial.Serial( serial_dev, 115200 )
      for num in command_list:
         ser.write(chr(num))
      ser.close()
      success = 1
   except:
      pass
   return success

# https://pymotw.com/2/socket/tcp.html
def main():
   # Create a TCP/IP socket
   print('starting up on %s port %s' % (service_addr, service_port) )
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.bind( ( service_addr, service_port ) )

   # Listen for incoming connections
   sock.listen(1)

   # Register service with zeroconf
   zeroconf.register_service(service_zc_info)

   while True:
      print('waiting for a connection')
      connection, client_address = sock.accept()

      try:
         print('connection from %s %s' % client_address)

         # Receive the data in small chunks and retransmit it
         while True:
            data = connection.recv(16)
            print('received "%s"' % data)
            if data:
               # Check commands to chars
               if roomba_commands.get( data, '' ):
                  # attempt to exec command
                  if roomba_do( roomba_commands.get( data, [] ) ):
                     connection.sendall('okay')
                  else: 
                     connection.sendall('whoops')
               else:
                  connection.sendall('eh?')
            else:
               print( 'no more data from %s %s' % client_address)
               break
            
      finally:
         # Unregister service with zeroconf
         zeroconf.unregister_service(service_zc_info)
         zeroconf.close()

         # Clean up the connection
         connection.close()

main()
