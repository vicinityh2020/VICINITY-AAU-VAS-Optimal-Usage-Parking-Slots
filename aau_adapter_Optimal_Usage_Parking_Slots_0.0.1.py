from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse
import requests
import socket   
import json
import time
import threading

#define global vars default state

Global_state_parking_sensor_1 = b'F'
Global_state_parking_sensor_2 = b'F'
Global_state_parking_sensor_3 = b'F'

stopflag = 0

#define global OID of devices
OID_Parking_Sensor_1 = '87bacf3e-ad0e-4120-938c-e01ce8014e16'
OID_Parking_Sensor_2 = 'f16b8c05-3bc0-4c81-b805-6dec543ba35b'
OID_Parking_Sensor_3 = 'f43c2e21-627c-44dd-b051-efd2ca4f29e3'


#Enquire data and state from EMS
#Publish events to subscribers through VICINITY agnet
def timerfun_publishevent():
   global Global_state_parking_sensor_1
   global Global_state_parking_sensor_2
   global Global_state_parking_sensor_3
   
   #Calculate number of free parking slot 
   FreeSlot= Global_state_parking_sensor_1 + Global_state_parking_sensor_2 + Global_state_parking_sensor_3 
   FreeSlot_string = str(FreeSlot, encoding = "utf-8")            
   FreeSlotNum = FreeSlot_string.count('F')     
   FreeSlotNum_byte = bytes(str(FreeSlotNum), encoding = "utf8")
    
   #Inquire state data from Labview for Charging price
   handel_TCPclient_interruptthread.send(b'Read_EMSstat_NNN') 
   responsestring = handel_TCPclient_interruptthread.recv(10) 

   #Rearrange received data from EMS
   chargeprice = responsestring[0:3]

   #Derive System time
   ISOTIMEFORMAT = '%Y-%m-%d %X'        
   systemtime = time.strftime(ISOTIMEFORMAT,time.localtime())
   systemtime = str(systemtime)
   systemtime = bytes(systemtime, encoding = "utf8")
   
   #Publish the Charing and parking status event
   hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_OUPS'}
   url = 'http://localhost:9997/agent/events/ParkingAndChargingStatus'  
   payload = b'{' + b'"value":"' + chargeprice + b'","free":"' +  FreeSlotNum_byte + b'","time":"'+ systemtime +b'"}'
   r=requests.request('PUT',url,headers=hd,data = payload)
   print(r.text)
   
   handel_timer_publishevent = threading.Timer(5,timerfun_publishevent,())         
   
   if stopflag==1:
        handel_timer_publishevent.cancel()
   else:
        handel_timer_publishevent.start()
   

#Handle the http requests from VICINITY agent 
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
 
        querypath = urlparse(self.path)
        path = str(querypath.path)
                
 
    def do_POST(self):
        
        global stopflag
        
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
                  
        string = body.decode() #encode()
        string = json.loads(string)
        
        control_ID=string['control_ID']
        control_val=string['value']
        
        if (control_ID=='shutdown' and control_val=='1'):
            response = BytesIO()
            response.write(b'HTTP/1.1 200 OK/Server is shutdown successfully')
            self.wfile.write(response.getvalue())   
            httpd.shutdown
            httpd.socket.close()            
            print('AAU adapter is shutdown successfully!')
            stopflag = 1
    
        else:
            response = BytesIO()
            response.write(b'HTTP/1.1 406 Failed')
            self.wfile.write(response.getvalue())   
 
    def do_PUT(self):
        
        global Global_state_parking_sensor_1
        global Global_state_parking_sensor_2
        global Global_state_parking_sensor_3
       
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
                    
        string = body.decode() #encode()
        string = json.loads(string)
        Sensor_ID=string['sensor_id']
        Sensor_State=string['value']
        
        if (Sensor_ID=='008000000400882f'):
            if(Sensor_State=='Occupied'):
                Global_state_parking_sensor_1 = b'O'
            else:
                Global_state_parking_sensor_1 = b'F'

        elif (Sensor_ID=='0080000004008835'):   
            if(Sensor_State=='Occupied'):
                Global_state_parking_sensor_2 = b'O'
            else:
                Global_state_parking_sensor_2 = b'F'
         
        elif (Sensor_ID=='008000000400884a'):
            if(Sensor_State=='Occupied'):
                Global_state_parking_sensor_3 = b'O'
            else:
                Global_state_parking_sensor_3 = b'F'
          
        else:
            response = BytesIO()
            response.write(b'HTTP/1.1 406 Failed')
            self.wfile.write(response.getvalue())  
                                   
        Finalsenddata = b'USet_ParkSen_' + Global_state_parking_sensor_1 + Global_state_parking_sensor_2 + Global_state_parking_sensor_3                     
        handel_TCPclient_mainthread.send(Finalsenddata)  

if __name__ == '__main__':
     #Create handel for TCP client to connect to Labview (main)  
     address = ('17486633in.iask.in', 31127)  
     handel_TCPclient_mainthread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
     handel_TCPclient_mainthread.connect(address) 

     #Create handel for TCP client to connect to Labview (interrupt)
     address = ('17486633in.iask.in', 36539 )  
     handel_TCPclient_interruptthread = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
     handel_TCPclient_interruptthread.connect(address) 
        
     #Open the channel for publishing the Charing and parking status event of AAU
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_OUPS'}
     url = 'http://localhost:9997/agent/events/ParkingAndChargingStatus'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #subscribe to the event of parking sensor 1(sensor_id:008000000400882f)           
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_OUPS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Parking_Sensor_1 + '/events/sensor-b4be8848-35bd-4720-9158-305d7e5c8c2b'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of parking sensor 2(sensor_id:0080000004008835)           
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_OUPS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Parking_Sensor_2 + '/events/sensor-849da2b0-8ed1-4d3b-bcac-46572b390acf'
     r=requests.request('POST',url,headers=hd)
     print(r.text)

     #subscribe to the event of parking sensor 3(sensor_id:008000000400884a)           
     hd = {'adapter-id':'AAU_Adapter','infrastructure-id':'VAS_OUPS'}
     url = 'http://localhost:9997/agent/objects/' + OID_Parking_Sensor_3 + '/events/sensor-64f41424-93ee-4130-8519-66a250f5bfe3'
     r=requests.request('POST',url,headers=hd)
     print(r.text)
     
     #start thread for publish event
     handel_timer_publishevent = threading.Timer(5,timerfun_publishevent,())  
     handel_timer_publishevent.start()

     #start main http server
     print('AAU Server is working!')
     httpd = HTTPServer(('localhost', 9995), SimpleHTTPRequestHandler)
     httpd.serve_forever()
    
  