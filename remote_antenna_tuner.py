import network
import socket
from time import sleep
from machine import Pin
import os
import json
from storage import Storage

class Stepper:
    def __init__(self, name:str, step_pin:Pin, dir_pin:Pin, counter=0):
        self.name = name
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.counter = counter
        self.step_pin.init(mode=Pin.OUT,value=1)
        self.dir_pin.init(mode=Pin.OUT,value=1)
        
    def rotate(self, direction, steps):
        print (f'Rotating : name: {self.name}, direction: {direction}, steps: {steps}')
        self.dir_pin.value(direction)
        stepper_enable.value(0)
        sleep(0.01)
   
        for step in range(0, steps):
            self.step_pin.value(1)
            sleep(0.01)
            self.step_pin.value(0)
            sleep(0.01)
            if (direction ):
                self.counter += 1
            else :
                self.counter -= 1
        sleep(0.1)
        stepper_enable.value(1)
        
    def set(self, new_position:int ):
        pass

class Memory:
    def __init__(self, steps1:int, steps2:int, steps3:int):
        # ToDo - read the initial value from a file holding the last readings before being switched off
        # self.name = name
        self.store(steps1, steps2, steps3)
        
    def store(self, steps1:int, steps2:int, steps3:int):
        self.steps1 = steps1
        self.steps2 = steps2
        self.steps3 = steps3
        pass
        
    def recall(self):
        return [ self.steps1,self.steps2,self.steps3]
    
# the pi pico is connected to a cheap CNC driver boad
# pins X,Y,Z step and X,Y,Z dir and one enable pin for all
# are connected to 9,8,7 step and 6,5,4 direction and 3 enable

motors = [Stepper('transmitter', Pin(9), Pin(6)),
          Stepper('antenna', Pin(8), Pin(5)),
          Stepper('inductance', Pin(7), Pin(4))]

# Each memory holds 3 step counts. Currently one for each transmitter, antenna and inductance
# ToDo - I've had to do this longhand, need to make the number of memories configurable 
memories = [Memory(20,78,100),
            Memory(15,65,50),
            Memory(0,0,0),
            Memory(0,0,0),
            Memory(0,0,0),
            Memory(0,0,0),
            Memory(0,0,0),            
            Memory(0,0,0)]

stepper_enable = Pin(3, Pin.OUT, value=1 )

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    #List all available networks
    networks = wlan.scan() # list with tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden    
    for w in networks:
        print(f'SSID: {w[0]},\t\t Channel: {w[2]},\t signal strength: {w[3]}' )


    print( f'Connecting to SSID: {nv_data.get_ssid()}')
    wlan.connect(str(nv_data.get_ssid()),  str(nv_data.get_password()) )
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form>
            <input type="submit" name='s_0_0_10' value="Stepper1 Backwards 10" />
            <input type="submit" name='s_0_0_1' value="Stepper1 Backwards 1" />
            <input type="submit" name='s_0_1_1' value="Stepper1 Foward 1" />
            <input type="submit" name='s_0_1_10' value="Stepper1 Foward 10" />
            </form>
            <form>
            <input type="submit" name='s_1_0_200' value="Stepper2 Backwards 1 turn" />
            <input type="submit" name='s_1_0_100' value="Stepper2 Backwards 0.5 turns" />
            <input type="submit" name='s_1_1_100' value="Stepper2 Foward 0.5 turns" />
            <input type="submit" name='s_1_1_200' value="Stepper2 Foward 1 turn" />
            </form>
            <form>
            <input type="submit" name='s_2_0_10' value="Stepper3 Backwards 10" />
            <input type="submit" name='s_2_0_1' value="Stepper3 Backwards 1" />
            <input type="submit" name='s_2_1_1' value="Stepper3 Foward 1" />
            <input type="submit" name='s_2_1_10' value="Stepper3 Foward 10" />
            </form>            
            <p>Stepper Motor 1 counter is {motors[0].counter}</p>
            <p>Stepper Motor 2 counter is {motors[1].counter}</p>
            <p>Stepper Motor 3 counter is {motors[2].counter}</p>
            <form>
            <input type="submit" name='m_0_0_0' value="Recall 160m Low" />
            <input type="submit" name='m_0_0_1' value="Recall 160m High" />
            <input type="submit" name='m_0_1_0' value="Save 160m Low" />
            <input type="submit" name='m_0_1_1' value="Save 160m High" />
            </form>
            <form>
            <input type="submit" name='m_0_0_2' value="Recall 80m Low" />
            <input type="submit" name='m_0_0_3' value="Recall 80m High" />
            <input type="submit" name='m_0_1_2' value="Save 80m Low" />
            <input type="submit" name='m_0_1_3' value="Save 80m High" />
            </form> 
            </body>
            </html>
            """
    return str(html)


def serve(connection):
    #Start a web server
    state = 'OFF'
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        name = request[2:].split('=')[0]
        if (len(name.split('_')) == 4):
            # name is f_s_d_n
            # f function - memory or stepper motor
            # s stepper motor number
            # d direction (0,1)
            # n number of turns
            f = str(name.split('_')[0])
            s = int(name.split('_')[1])
            d = int(name.split('_')[2])
            n = int(name.split('_')[3])
            #process name to move stepper motor
            if f == 's':
                motors[s].rotate(d,n)
                #save_motor_positions(motors[0].counter,motors[1].counter,motors[2].counter)
                stepper_positions = [motors[0].counter, motors[1].counter, motors[2].counter]
                nv_data.write_current_steppers( file, stepper_positions )
                #nv_data.write_current_steppers( file, [motors[0].counter,motors[1].counter,motors[2].counter] )
                
            elif f == 'm':
                # process name to change stepper motor position memory
                # where s is ignored, d=0 ( recall ) d=1 ( write ), n is memory number
                if ( d ):
                    #save memory
                    memories[n].store( motors[0].counter,motors[1].counter,motors[2].counter )

                else:
                    # recall stepper value for this frequency, workout the change required to go there
                    for each_motor in range(3):
                        offset = memories[n].recall()[each_motor] - motors[each_motor].counter
                        #for the capacitors, they only should be set 0 - 100 as they are only useful over 180 degrees
                        #and capacitors should not be sent to negative settings - it will work but will only confuse the situation
                        #the inductor ( rollercoaster ) should not try to go to a negative reason. Mechanically it cannot go to a negative position 
                        if ( offset >= 0 ):
                            motors[each_motor].rotate(1,offset)
                        elif ( offset <=0 ):
                            motors[each_motor].rotate(0,abs(offset))
                            
                        nv_data.write_current_steppers( file, [motors[0].counter,motors[1].counter,motors[2].counter])
                        #save_motor_positions(motors[0].counter,motors[1].counter,motors[2].counter)
                
        else:
            pass
            #print('name length incorrect')
        
        
        html = webpage(temperature, state)
        client.send(html)
        client.close()


file = 'xyzzy.txt'
nv_data = Storage(file)

try:
    ip=connect()
    connection=open_socket(ip)
    serve(connection)
    connection.close()
    
except KeyboardInterrupt:
    machine.reset()