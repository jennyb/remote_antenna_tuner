#based on micropython/examples/pico_display/button_test.py
import time
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4

# using this hardware https://shop.pimoroni.com/products/pico-display-pack-2-0?variant=39374122582099
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_P4, rotate=0)

display.set_backlight(0.5)
display.set_font("sans")
display.set_thickness(2)

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)

# sets up a handy function we can call to clear the screen
def clear():
    display.set_pen(BLACK)
    display.clear()
    display.update()

def display_steppers(ip_address,stepper_values,steps_per_push,memory_number):
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(GREEN)
    display.rectangle(0, ((selected_stepper_motor+1) * 40), 320, 40)
    display.set_pen(MAGENTA)
    display.text(f"IP: {ip_address}", 0, 20, 320, scale=1 )
    display.set_pen(WHITE)    
    display.text(f"Stepper 1: { stepper_values[0] }", 0, 60, 320, scale=1)
    display.text(f"Stepper 2: { stepper_values[1] }", 0, 100, 320, scale=1)
    display.text(f"Stepper 3: { stepper_values[2] }", 0, 140, 320, scale=1)
    display.text(f"Steps: { steps_per_push }", 0, 180, 320, scale=1)
    display.text(f"Memory: { memory_number }", 0, 220, 320, scale=1)
    display.update()

def set_ip(ipaddress):
    pass

def set_steppers(stepper_values):
    pass


# set up
clear()
selected_stepper_motor = 0
steppers = [0,0,0]
ip_address = "192.168.2.100"
steps_per_push = 1
memory_number = 1
steps_field_selected = 0 # this is non zero when the display field is selected 
memory_field_selected = 0 # # this is non zero when the memory field is selected 
display_steppers(ip_address,steppers, steps_per_push, memory_number)


    
while True:
    # button A selects which stepper motor to use, it will cycle through 1,2,3,1 etc
    if button_a.read(): 
        selected_stepper_motor += 1
        selected_stepper_motor =  selected_stepper_motor %5
        if ( selected_stepper_motor == 3):
            # steps field selected. options are 1,10,1000 per press
            steps_field_selected = 1
            memory_field_selected = 0
        elif ( selected_stepper_motor == 4):
            # memory selected 0 .. 9
            steps_field_selected = 0
            memory_field_selected = 1
        else:
           # stepper live control selected
            steps_field_selected = 0
            memory_field_selected = 0            
            
        display_steppers(ip_address,steppers,steps_per_push, memory_number)

    elif button_b.read():
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(MAGENTA)
        display.text("Do not  ", 0, 30, 320, scale=2)
        display.text("press this ", 0, 80, 320, scale=2)        
        display.text("button ", 0, 140, 320, scale=2)
        display.text("again !", 0, 200, 320, scale=2)        
        display.update()
        pass
    
    elif button_x.read():
        if ( (steps_field_selected == 0) and (memory_field_selected == 0) ):
            steppers[selected_stepper_motor] += steps_per_push
            display_steppers(ip_address,steppers, steps_per_push,memory_number)
        elif ( (steps_field_selected == 1) and (memory_field_selected == 0) ):
            steps_per_push = steps_per_push * 10
        elif ( (steps_field_selected == 0) and (memory_field_selected == 1) ):
            memory_number += 1

    elif button_y.read():
        if ( (steps_field_selected == 0) and (memory_field_selected == 0) ):
            steppers[selected_stepper_motor] -= steps_per_push
            display_steppers(ip_address,steppers,steps_per_push,memory_number)
        elif ( (steps_field_selected == 1) and (memory_field_selected == 0) ):
                       steps_per_push = steps_per_push / 10
        elif ( (steps_field_selected == 0) and (memory_field_selected == 1) ):
            memory_number -= 1
            
    else:
        pass
        #display.set_pen(GREEN)
        #display.text("Unknown button!", 10, 10, 240, 4)
        #display.update()
    time.sleep(0.1)  # this number is how frequently the Pico checks for button presses
