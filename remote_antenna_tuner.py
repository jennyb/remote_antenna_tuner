import network
import socket
from time import sleep
from machine import Pin
import os
import json
from storage import Storage
import display_handling 

# Hardware
# Display LED R 9
# Display LED B 10
# Display LED B 11
# Display LCD_TE 27
# Display Backlight En 26
# Display LCD_MOSI 25
# Display LCD_SCLK 24
# Display LCD_CS 22
# Display LCD_DC 21
button_a = Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)
button_b = Pin(13, mode=Pin.IN, pull=Pin.PULL_UP)
button_x = Pin(14, mode=Pin.IN, pull=Pin.PULL_UP)
button_y = Pin(15, mode=Pin.IN, pull=Pin.PULL_UP)
stepper_enable = Pin(3, Pin.OUT, value=1 ) 	# active low. The current cnc interface board has one common stepper motor driver enble line.
                                            # this is the current cnc interface https://www.az-delivery.uk/products/az-delivery-cnc-shield-v3
                                            # My new PCB will have one enable for each stepper motor driver

# transmitter step Pin(9)
# transmitter dir  Pin(6)
# antenna step     Pin(8)
# antenna dir      Pin(5)
# inductance step  Pin(7)
# inductance dir   Pin(4)
led = Pin("LED", Pin.OUT)





def button_a_isr(pin):
    user_display.button_a_pressed()
    #pin_led.value(not pin_led.value())
    
def button_b_isr(pin):
    user_display.button_b_pressed()    

def button_x_isr(pin):
    user_display.button_x_pressed()

def button_y_isr(pin):
    user_display.button_y_pressed()

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
        stepper_enable.value(0) # set the hardware enable to be active low 
        sleep(0.01)
   
        for step in range(0, steps):
            if (direction ):
                self.counter += 1
            else :
                # this is where we stop the stepper motor going to a negative value
                # for a rollercoaster tuning inductor this would just hit the zero end stop and be meaningless
                # for a variable capacitor, they are only useful between 0 and 180 degrees.
                # Outside this they are just repeating the same capacitance 
                if self.counter > 0: 
                    self.counter -= 1
                else:
                    break # drop out of the For loop, because we do not want to reverse the motor beyond/before 0
            self.step_pin.value(1)
            sleep(0.01)
            self.step_pin.value(0)
            sleep(0.01)

                    
        sleep(0.1)
        stepper_enable.value(1) # set the hardware enable to be inactive high
        
    def set(self, new_position:int ):
        pass


motors = [Stepper('transmitter', Pin(9), Pin(6)),
          Stepper('antenna', Pin(8), Pin(5)),
          Stepper('inductance', Pin(7), Pin(4))]

# ToDo - Make the number of memories configurable 

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    
    # List all available networks
    # if no networks are available, wait then try again. 
    # networks is an array of tupples with 6 fields ssid, bssid, channel, RSSI, security, hidden 
    while True :
        networks = wlan.scan()

        number_of_networks = len(networks)     
        if number_of_networks == 0:
            # make an empty network to display that there is no network.
            networks = [('None',0,0,0,0,0)]
            user_display.display_networks(networks)
            sleep(10)
        else :
            # at least one network has been found ( it may not include the one that we want )      
            for w in networks:
                print(f'SSID: {w[0]},\t\t Channel: {w[2]},\t signal strength: {w[3]}\n' )
            user_display.display_networks(networks)
            break
    

    print( f'Connecting to SSID: {nv_data.get_ssid()}')
    wlan.connect(str(nv_data.get_ssid()),  str(nv_data.get_password()) )
    
    connection_timeout = 20      # sometimes the wlan keep trying and never gets a connection. Reset the Pico after 10 tries
    while wlan.isconnected() == False:
        connection_timeout -= 1
        if not connection_timeout :
            print('reboot forced due to no wlan connection')
            sleep(5)
            machine.reset()    
        print(f'Waiting for IP address. {connection_timeout} seconds left')
        sleep(1)
      
    ip = wlan.ifconfig()[0]
    # turn on the onboard LED to show network connection - useful with no display
    led.on()
    user_display.set_ip(ip)
    # update display to show IP AND signal level
    print(f'Connected on {ip}')
    return ip


def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    try :
        connection.bind(address) # errors to be caught : File "<stdin>", line 314, in <module>  File "<stdin>", line 151, in open_socket OSError: [Errno 98] EADDRINUSE
    except:
        print('reboot forced due to socket already open')
        sleep(5)
        machine.reset()  
    connection.listen(1)
    return connection


def webpage(state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
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
            <form>
            <input type="submit" name='m_0_0_4' value="Recall 60m Low" />
            <input type="submit" name='m_0_0_5' value="Recall 60m High" />
            <input type="submit" name='m_0_1_4' value="Save 60m Low" />
            <input type="submit" name='m_0_1_5' value="Save 60m High" />
            </form>
            <form>
            <input type="submit" name='m_0_0_6' value="Recall 40m Low" />
            <input type="submit" name='m_0_0_7' value="Recall 40m High" />
            <input type="submit" name='m_0_1_6' value="Save 40m Low" />
            <input type="submit" name='m_0_1_7' value="Save 40m High" />
            </form>
            <form>
            <input type="submit" name='m_0_0_8' value="Recall 30m Low" />
            <input type="submit" name='m_0_0_9' value="Recall 30m High" />
            <input type="submit" name='m_0_1_8' value="Save 30m Low" />
            <input type="submit" name='m_0_1_9' value="Save 30m High" />
            </form>
            
            <form>
            <input type="submit" name='z_0_0_0' value="Zero all capacitors and rollercoaster" />
            </form>
            
            </body>
            </html>
            """
    return str(html)

def header(state):
    #Template HTML
    html = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'

    return str(html)



def serve(connection):
    #Start a web server
    state = 'OFF'
    while True:
        client = connection.accept()[0]
        request = client.recv(1024) # error to handle  File "<stdin>", line 315, in <module>  File "<stdin>", line 233, in serve
        request = str(request)
        print('HTTP client request')
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
                user_display.set_steppers( stepper_positions )
                #nv_data.write_current_steppers( file, [motors[0].counter,motors[1].counter,motors[2].counter] )
                
            elif f == 'm':
                # process name to change stepper motor position memory
                # where s is ignored, d=0 ( recall ) d=1 ( write ), n is memory number
                if ( d ):
                    #save memory
                    nv_data.write_memory(file, n, [motors[0].counter,motors[1].counter,motors[2].counter])
                    #memories[n].store( motors[0].counter,motors[1].counter,motors[2].counter )

                else:
                    # recall stepper value for this frequency, workout the change required to go there
                    for each_motor in range(3):
                        offset = nv_data.get_memory(n)[each_motor] - motors[each_motor].counter
                        #for the capacitors, they only should be set 0 - 100 as they are only useful over 180 degrees
                        #and capacitors should not be sent to negative settings - it will work but will only confuse the situation
                        #the inductor ( rollercoaster ) should not try to go to a negative reason. Mechanically it cannot go to a negative position 
                        if ( offset >= 0 ):
                            motors[each_motor].rotate(1,offset)
                        elif ( offset <=0 ):
                            motors[each_motor].rotate(0,abs(offset))
                            
                        nv_data.write_current_steppers( file, [motors[0].counter,motors[1].counter,motors[2].counter])

            elif f == 'z':
                #zero the stepper motors and set the mv ram appropriately
                print('Zero the motors and update the nvram')
                for each_motor in range(3):
                        offset = 0 - motors[each_motor].counter

                        if ( offset >= 0 ):
                            motors[each_motor].rotate(1,offset)
                        elif ( offset <=0 ):
                            motors[each_motor].rotate(0,abs(offset))
                            
                        nv_data.write_current_steppers( file, [0,0,0])


        else:
            pass
            #print('name length incorrect')
        
        html = header(state)
        client.send(html)
        sleep(1)
        html = webpage(state)
        client.send(html)
        client.close()


#main code
#we might need a watchdog timer at some point
#from machine import WDT
#wdt = WDT(timeout=2000)  # enable it with a timeout of 2s
#wdt.feed()


button_a.irq(trigger=Pin.IRQ_FALLING,handler=button_a_isr)
button_b.irq(trigger=Pin.IRQ_FALLING,handler=button_b_isr)
button_x.irq(trigger=Pin.IRQ_FALLING,handler=button_x_isr)
button_y.irq(trigger=Pin.IRQ_FALLING,handler=button_y_isr)

# interrupt boot if button_a pressed - when this file has been renamed main.py it is difficult to get out of the loop
# in order to update software

sleep(5)
if ( button_a == 0 ) :
    exit()

file = 'xyzzy.txt'
nv_data = Storage(file)
user_display = display_handling.LocalDisplay(nv_data.get_stepper_positions())
[motors[0].counter, motors[1].counter, motors[2].counter] = nv_data.get_stepper_positions()
#ser_display.set_steppers(nv_data.get_stepper_positions())


try:
    ip=connect()
    connection=open_socket(ip) 
    serve(connection)
    connection.close()
    
except KeyboardInterrupt:
    connection.close()
    machine.reset()