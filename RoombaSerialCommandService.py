#!/usr/bin/env python
__author__ = 'Jon Stratton'
import socket, serial
from zeroconf import ServiceInfo, Zeroconf
from flask import Flask  

service_name = 'Roomba Serial Command'

# Roomba device settings
serial_dev = '/dev/ttyUSB0'

# Roomba commands to char
roomba_commands = {
   'clean': [128, 131, 135],
   'spot' : [128, 131, 134],
   'dock' : [128, 131, 143],
   'off'  : [128, 131, 133],
}

# Hardcode as needed
service_port = 20807
fqdn = socket.gethostname()
service_addr = socket.gethostbyname(fqdn)
service_host = fqdn.split('.')[0]

# Zeroconf Service settings
service_zc_desc = {'service': service_name, 'version': '0.1'}
service_zc_info = ServiceInfo('_http._tcp.local.',
                   service_host + ' ' + service_name + '._http._tcp.local.',
                   socket.inet_aton(service_addr), service_port, 0, 0, service_zc_desc)
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

app = Flask(__name__) 

@app.route("/do/<string:command>/")
def do(command):
    ret_str = 'eh?'
    if roomba_commands.get( command, [] ):
       if roomba_do( roomba_commands.get( command, [] ) ):
          ret_str = 'okay'
       else:
          ret_str = 'whoops'
    return ret_str

@app.route('/')
def home():  
    return "Hello"

if __name__ == "__main__": 
    # Reg service
    zeroconf.register_service(service_zc_info)

    app.run(host='0.0.0.0', port=service_port, debug=False)
