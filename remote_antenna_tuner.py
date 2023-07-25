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
stepcounter = 0 

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
            <input type="submit" name='a' value="Step Backwards 10" />
            <input type="submit" name='b' value="Step Backwards 1" />
            <input type="submit" name='c' value="Step Foward 1" />
            <input type="submit" name='d' value="Step Foward 10" />
            </form>
            <p>stepcounter is {stepcounter}</p>
            <p>Temperature is {temperature}</p>
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
        print(request)
        if request == '/?c=Step+Foward+1':
            rotate(1,0)
        elif request =='/?d=Step+Foward+10':
            rotate(10,0)
        elif request =='/?b=Step+Backwards+1':
            rotate(1,1)
        elif request =='/?a=Step+Backwards+10':
            rotate(10,1)    
        html = webpage(temperature, state)
        client.send(html)
        client.close()

def rotate(steps,direction):
    global stepcounter
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
            stepcounter -= 1
        else :
            stepcounter += 1
    sleep(0.1)
    stepper_enable.value(1)

try:
    ip=connect()
    connection=open_socket(ip)
    serve(connection)
    
    
except KeyboardInterrupt:
    machine.reset()