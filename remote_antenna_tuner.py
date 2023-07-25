import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
from machine import Pin


stepper_enable = Pin(2, Pin.OUT, value=1 )
stepper_dir_pin = machine.Pin(3,machine.Pin.OUT, value=1)
stepper_step_pin = machine.Pin(4,machine.Pin.OUT, value=1)
ssid = 'J2N2'
password = 'arduin0c00kb00k'
stepcounter1 = 0
stepcounter2 = 0
stepcounter3 = 0 

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
            <input type="submit" name='1_0_10' value="Stepper1 Backwards 10" />
            <input type="submit" name='1_0_1' value="Stepper1 Backwards 1" />
            <input type="submit" name='1_1_1' value="Stepper1 Foward 1" />
            <input type="submit" name='1_1_10' value="Stepper1 Foward 10" />
            </form>
            <form>
            <input type="submit" name='2_0_10' value="Stepper2 Backwards 10" />
            <input type="submit" name='2_0_1' value="Stepper2 Backwards 1" />
            <input type="submit" name='2_1_1' value="Stepper2 Foward 1" />
            <input type="submit" name='2_1_10' value="Stepper2 Foward 10" />
            </form>
            <form>
            <input type="submit" name='3_0_10' value="Stepper3 Backwards 10" />
            <input type="submit" name='3_0_1' value="Stepper3 Backwards 1" />
            <input type="submit" name='3_1_1' value="Stepper3 Foward 1" />
            <input type="submit" name='3_1_10' value="Stepper3 Foward 10" />
            </form>            
            <p>Stepper Motor 1 counter is {stepcounter1}</p>
            <p>Stepper Motor 2 counter is {stepcounter2}</p>
            <p>Stepper Motor 2 counter is {stepcounter3}</p>            
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
            rotate(n,d)
        
        html = webpage(temperature, state)
        client.send(html)
        client.close()

def rotate(steps,direction):
    global stepcounter1
    global stepcounter2
    global stepcounter3    
    stepper_dir_pin.value(direction)
    sleep(0.01)
    stepper_enable.value(0)
    sleep(0.01)
    for step in range(0, steps):
        stepper_step_pin.value(1)
        sleep(0.01)
        stepper_step_pin.value(0)
        sleep(0.01)
        if (direction ):
            stepcounter1 += 1
        else :
            stepcounter1 -= 1
    sleep(0.1)
    stepper_enable.value(1)

try:
    ip=connect()
    connection=open_socket(ip)
    serve(connection)
    
    
except KeyboardInterrupt:
    machine.reset()