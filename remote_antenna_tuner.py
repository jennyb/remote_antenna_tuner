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
        print (self.name,direction, steps, self.step_pin, self.dir_pin)
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
    
ssid = 'J2N2'
password = 'arduin0c00kb00k'

# the pi pico is connected to a cheap CNC driver boad
# pins X,Y,Z step and X,Y,Z dir and one enable pin for all
# are connected to 9,8,7 step and 6,5,4 direction and 3 enable

motors = [Stepper('transmitter', Pin(9), Pin(6)),
          Stepper('antenna', Pin(8), Pin(5)),
          Stepper('inductance', Pin(7), Pin(4))]

stepper_enable = Pin(3, Pin.OUT, value=1 )

file = 'config.txt'


#https://forums.raspberrypi.com/viewtopic.php?t=340983
def get_config_default(file):
    try:
        with open(file) as fd:
            return json.load(fd)

    except OSError:
        with open(file, "w") as fd:
            config = {
                "stepper1_en": 1,
                "stepper1_dir": 6,
                "stepper1_step": 7,
                "ssid": "default network",
                "password": "default password",
            }
            json.dump(config, fd)
            return config



def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
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
            <input type="submit" name='0_0_10' value="Stepper1 Backwards 10" />
            <input type="submit" name='0_0_1' value="Stepper1 Backwards 1" />
            <input type="submit" name='0_1_1' value="Stepper1 Foward 1" />
            <input type="submit" name='0_1_10' value="Stepper1 Foward 10" />
            </form>
            <form>
            <input type="submit" name='1_0_200' value="Stepper2 Backwards 1 turn" />
            <input type="submit" name='1_0_100' value="Stepper2 Backwards 0.5 turns" />
            <input type="submit" name='1_1_100' value="Stepper2 Foward 0.5 turns" />
            <input type="submit" name='1_1_200' value="Stepper2 Foward 1 turn" />
            </form>
            <form>
            <input type="submit" name='2_0_10' value="Stepper3 Backwards 10" />
            <input type="submit" name='2_0_1' value="Stepper3 Backwards 1" />
            <input type="submit" name='2_1_1' value="Stepper3 Foward 1" />
            <input type="submit" name='2_1_10' value="Stepper3 Foward 10" />
            </form>            
            <p>Stepper Motor 1 counter is {motors[0].counter}</p>
            <p>Stepper Motor 2 counter is {motors[1].counter}</p>
            <p>Stepper Motor 3 counter is {motors[2].counter}</p>
            <form>
            <input type="submit" name='4_0_0' value="Recall 160m Low" />
            <input type="submit" name='4_0_1' value="Recall 160m High" />
            <input type="submit" name='4_0_2' value="Save 160m Low" />
            <input type="submit" name='4_0_3' value="Save 160m High" />
            </form>
            <form>
            <input type="submit" name='4_0_0' value="Recall 80m Low" />
            <input type="submit" name='4_0_1' value="Recall 80m High" />
            <input type="submit" name='4_0_2' value="Save 80m Low" />
            <input type="submit" name='4_0_3' value="Save 80m High" />
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
        if (len(name.split('_')) == 3):
            # name is s_d_n
            # s servo number
            # d direction (0,1)
            # n number of turns
            s = int(name.split('_')[0])
            d = int(name.split('_')[1])
            n = int(name.split('_')[2])
            motors[s].rotate(d,n)
        
        html = webpage(temperature, state)
        client.send(html)
        client.close()

get_config_default(file)

try:
    ip=connect()
    connection=open_socket(ip)
    serve(connection)
    connection.close()

    
except KeyboardInterrupt:

    machine.reset()