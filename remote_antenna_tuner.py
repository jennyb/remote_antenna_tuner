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
            <form action="./lighton">
            <input type="submit" value="Light on" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="Light off" />
            </form>
            <p>LED is {state}</p>
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
        if request == '/lighton?':
            rotate(200,0)
        elif request =='/lightoff?':
            rotate(10,0)
        html = webpage(temperature, state)
        client.send(html)
        client.close()

def rotate(steps,dir):
    stepper_dir_pin.value(dir)
    sleep(0.01)
    stepper_enable.value(0)
    sleep(0.01)
    for step in range(0, steps):
        stepper_step_pin.value(1)
        sleep(0.01)
        stepper_step_pin.value(0)
        sleep(0.01)
    sleep(0.1)
    stepper_enable.value(1)

try:
    ip=connect()
    connection=open_socket(ip)
    serve(connection)
    
    
except KeyboardInterrupt:
    machine.reset()