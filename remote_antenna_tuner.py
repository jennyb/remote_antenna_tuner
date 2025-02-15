import network
from time import sleep
from machine import Pin
import os
import json
from storage import Storage
import display_handling 
import uasyncio as asyncio

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

motors = [Stepper('transmitter', Pin(9), Pin(6)),
          Stepper('antenna', Pin(8), Pin(5)),
          Stepper('inductance', Pin(7), Pin(4))]

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




"""
    Return the static HTML page
"""
def webpage():
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
    return html

"""
    Return a HTML header
"""
def header():
    #Template HTML
    html = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'
    return html

#
# Connect to the wireless network, or raise an exception
#
def connect_to_network(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm = 0xa11140) # Disable power-save mode
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
    max_wait -= 1
    print('waiting for connection...')
    sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

"""
    We have found a request to move servos
"""

def process_request(name):
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


async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    request_line = str(request_line)
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    try:
        request_line = request_line.split()[1]
    except IndexError:
        pass
    
    print("line:", request_line)
    name = request_line[2:].split('=')[0]
    process_request(name)
    
    writer.write(header())
    writer.write(webpage())

    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")
    
    
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

print('Loading config file...')
file = 'xyzzy.txt'
nv_data = Storage(file)
user_display = display_handling.LocalDisplay(nv_data.get_stepper_positions())
[motors[0].counter, motors[1].counter, motors[2].counter] = nv_data.get_stepper_positions()
#ser_display.set_steppers(nv_data.get_stepper_positions())
    
async def main():
    print('Loading config file...')
    file = 'xyzzy.txt'
    nv_data = Storage(file)
    user_display = display_handling.LocalDisplay(nv_data.get_stepper_positions())
    [motors[0].counter, motors[1].counter, motors[2].counter] = nv_data.get_stepper_positions()
    #ser_display.set_steppers(nv_data.get_stepper_positions())

    print('Connecting to Network...')
    connect_to_network(nv_data.get_ssid(), nv_data.get_password())

    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    while True:
        await asyncio.sleep(5)

    try:
        asyncio.run(main())
    finally:
        asyncio.new_event_loop()

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
    
