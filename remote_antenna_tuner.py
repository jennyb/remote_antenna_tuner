import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
from machine import Pin
import os
import json


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
# ToDo - I've had to do this longhand because I don't understant arrays in python
memories = [Memory(20,78,100),
            Memory(15,65,50),
            Memory(0,0,0),
            Memory(0,0,0),
            Memory(0,0,0)]

stepper_enable = Pin(3, Pin.OUT, value=1 )


#This file holds config, stepper motor positions and memories
file = 'xyzzy.txt'
# https://forums.raspberrypi.com/viewtopic.php?t=340983
def get_config_default(file):
    try:
        with open(file) as fd:
            return json.load(fd)
            fd.close()

    except OSError:
        with open(file, "w") as fd:
            config = {
                "stepper1_stored_pos": 0,
                "stepper2_stored_pos": 0,
                "stepper3_stored_pos": 0,
                "ssid": "default",
                "password": "default",
            }
            json.dump(config, fd)
            fd.close()
            return config


def save_motor_positions(file,x,y,z):
    with open(file, "w") as fd:
        config["stepper0_stored_pos"] = motors[0].counter
        config["stepper1_stored_pos"] = motors[1].counter
        config["stepper2_stored_pos"] = motors[2].counter
        json.dump(config, fd)
        fd.close()


def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config["ssid"] ,  config["password"] )
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
    pico_led.off()
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
        print(name)
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
                save_motor_positions(file,motors[0].counter,motors[1].counter,motors[2].counter)
                
            elif f == 'm':
                # process name to change stepper motor position memory
                # where s is ignored, d=0 ( recall ) d=1 ( write ), n is memory number
                print(f,s,d,n)
                if ( d ):
                    print('write stepper values into memory')
                    memories[n].store( motors[0].counter,motors[1].counter,motors[2].counter )
                    print(motors[0].counter,motors[1].counter,motors[2].counter)
                else:
                    # recall stepper value for this frequency, workout the change required to go there
                    print('recall stepper values from memory, compare to existing location and change')
                    print(memories[n].recall())
                    for each_motor in range(3):
                        offset = memories[n].recall()[each_motor] - motors[each_motor].counter
                        print (f'motor number: {each_motor}')
                        print (f'current location: {motors[each_motor].counter}')
                        print (f'memorised new location: {memories[n].recall()[each_motor]}')
                        print (f'required offset:  {offset} {abs(offset)}')
                        if ( offset >= 0 ):
                            motors[each_motor].rotate(1,offset)
                        elif ( offset <=0 ):
                            motors[each_motor].rotate(0,abs(offset))
                        save_motor_positions(file,motors[0].counter,motors[1].counter,motors[2].counter)
        else:
            pass
            #print('name length incorrect')
        
        
        html = webpage(temperature, state)
        client.send(html)
        client.close()

config = get_config_default(file)
print( config )
motors[0].counter = config["stepper0_stored_pos"]
motors[1].counter = config["stepper1_stored_pos"]
motors[2].counter = config["stepper2_stored_pos"]

try:
    ip=connect()
    connection=open_socket(ip)
    serve(connection)
    connection.close()

    
except KeyboardInterrupt:

    machine.reset()