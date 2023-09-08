#based on micropython/examples/pico_display/button_test.py
import time
#from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2, PEN_P4


# ToDo set limits to the steppers and variable capacitors. Variable capacitors are only useful over 180 degrees = 100 steps

class LocalDisplay:

    def __init__(self, incomming_stepper_values):

        self.stepper_values =  incomming_stepper_values # current location of each stepper motors in steps where one full rotation = 200 steps 
        self.ip_address = "0.0.0.0" # set by the wifi code and just dumbly displayed to the user
        self.steps_per_push = 1
        self.memory_number = 1
        self.steps_field_selected = 0 # this is non zero when the display field is selected 
        self.memory_field_selected = 0 # # this is non zero when the memory field is selected
        self.selected_stepper_motor = 0

        # using this hardware https://shop.pimoroni.com/products/pico-display-pack-2-0?variant=39374122582099
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY_2, pen_type=PEN_P4, rotate=0)
        
        self.WHITE = self.display.create_pen(255, 255, 255)
        self.BLACK = self.display.create_pen(0, 0, 0)
        self.CYAN = self.display.create_pen(0, 255, 255)
        self.MAGENTA = self.display.create_pen(255, 0, 255)
        self.YELLOW = self.display.create_pen(255, 255, 0)
        self.GREEN = self.display.create_pen(0, 255, 0)
        
        self.display.set_backlight(0.5)
        self.display.set_font("sans")
        self.display.set_thickness(2)

        # attach each button to a GPIO so that it can be polled
        # ToDo - make these interrupt based
        #self.button_a = Button(12)
        #self.button_b = Button(13)
        #self.button_x = Button(14)
        #self.button_y = Button(15)



    # Sets the pen colour to black then uses that to paint the whole screen black, not forgetting to update the display
    def clear(self):
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.update()

    # once a vaiable has been changed, update the display from the instance's local variables
    def display_steppers(self):
        self.clear()
        self.display.set_pen(self.GREEN)
        self.display.rectangle(0, ((self.selected_stepper_motor+1) * 40), 320, 40)
        self.display.set_pen(self.MAGENTA)
        self.display.text(f"IP: {self.ip_address}", 0, 20, 320, scale=1 )
        self.display.set_pen(self.WHITE)    
        self.display.text(f"Stepper 1: { self.stepper_values[0] }", 0, 60, 320, scale=1)
        self.display.text(f"Stepper 2: { self.stepper_values[1] }", 0, 100, 320, scale=1)
        self.display.text(f"Stepper 3: { self.stepper_values[2] }", 0, 140, 320, scale=1)
        self.display.text(f"Steps: { self.steps_per_push }", 0, 180, 320, scale=1)
        self.display.text(f"Memory: { self.memory_number }", 0, 220, 320, scale=1)
        self.display.update()

    def set_ip(self,ipaddress):
        self.ip_address = ipaddress
        self.display_steppers()

    def display_networks(self, networks):
        self.clear()
        self.display.set_pen(self.WHITE)
        
        #sort by signal strength. -50dBm is stronger than -80dBm
        networks.sort(reverse = True, key=lambda a: a[3])
        
        number_of_networks = len(networks)
        network_fields = len(networks[0])
        if (number_of_networks > 0 ) and ( network_fields > 0 ):
            for ssid in range (number_of_networks):
                # ToDo failing to convert byte array from the SSID to a string for the LCD display 
                ssid_name = networks[ssid][0].decode('utf-8')
                ssid_channel = networks[ssid][2]
                ssid_sig = networks[ssid][3]
                self.display.text(f'{ssid_name} {ssid_sig}dBm, Ch{ssid_channel}', 0, 20+(40*ssid), 320, scale=1 )
            self.display.update()

    def set_steppers(self,stepper_input_values):
        self.stepper_values = stepper_input_values
        self.display_steppers()        


    def set_memory(self,mem_no):
        self.memory_number = mem_no
        self.display_steppers()

    def button_a_pressed(self):
        self.selected_stepper_motor += 1
        self.selected_stepper_motor =  self.selected_stepper_motor %5
        if ( self.selected_stepper_motor == 3):
            # steps field selected. options are 1,10,1000 per press
            self.steps_field_selected = 1
            self.memory_field_selected = 0
        elif ( self.selected_stepper_motor == 4):
            # memory selected 0 .. 9
            self.steps_field_selected = 0
            self.memory_field_selected = 1
        else:
            # stepper live control selected
            self.steps_field_selected = 0
            self.memory_field_selected = 0            
                    
        self.display_steppers()    

    def button_b_pressed(self):
        self.display.set_pen(self.BLACK)
        self.display.clear()
        self.display.set_pen(self.MAGENTA)
        self.display.text("Do not  ", 0, 30, 320, scale=2)
        self.display.text("press this ", 0, 80, 320, scale=2)        
        self.display.text("button ", 0, 140, 320, scale=2)
        self.display.text("again !", 0, 200, 320, scale=2)        
        self.display_steppers()
        
    def button_x_pressed(self):
        if ( (self.steps_field_selected == 0) and (self.memory_field_selected == 0) ):
            self.stepper_values[self.selected_stepper_motor] += self.steps_per_push
        elif ( (self.steps_field_selected == 1) and (self.memory_field_selected == 0) ): # ToDo make sure that only steps per push can equal 1,10,100 0r 1000
            self.steps_per_push = self.steps_per_push * 10
        elif ( (self.steps_field_selected == 0) and (self.memory_field_selected == 1) ): # ToDo Make sure memory number is valid
            self.memory_number = self.memory_number + 1
        self.display_steppers()    
    
    def button_y_pressed(self):
        # ToDo the stepper motor can never move backwards to below zero
        if ((self.steps_field_selected == 0) and (self.memory_field_selected == 0)): 
            if ( self.stepper_values[self.selected_stepper_motor] - self.steps_per_push ) > 0:
                self.stepper_values[self.selected_stepper_motor] -= self.steps_per_push # verify this does not go below zero
            else :
                self.stepper_values[self.selected_stepper_motor] = 0
        elif ( (self.steps_field_selected == 1) and (self.memory_field_selected == 0) ): # ToDo make sure that only steps per push can equal 1,10,100 0r 1000
            self.steps_per_push = self.steps_per_push / 10
        elif ( (self.steps_field_selected == 0) and (self.memory_field_selected == 1) ): # ToDo Make sure memory number is valid
            self.memory_number = self.memory_number - 1
        self.display_steppers()                      


if __name__ == '__main__':
    user_display = LocalDisplay([0,0,0])

    user_display.set_ip('1.1.1.1')
    user_display.set_memory('3')
    user_display.set_steppers([1,2,3])    
    user_display.button_x_pressed()
    time.sleep(1)

    user_display.button_a_pressed()
    user_display.button_a_pressed()
    user_display.button_a_pressed()
    user_display.button_x_pressed()
    time.sleep(1)    

    user_display.button_a_pressed()    
    user_display.button_a_pressed()    
    user_display.button_y_pressed()
    time.sleep(1)    
    
    user_display.set_steppers([1,2,3])
    time.sleep(1)    
    user_display.set_steppers([4,5,6])
    time.sleep(1)    
    user_display.set_steppers([7,8,9])
    time.sleep(1)
    
    network_display = [[b'J2N2', 0, 3, -67], [b'Test', 0, 1, -84], [b'BT-RTAH93', 0, 1, -82], [b'BTWi-fi', 0, 1, -85], [b'J2', 0, 3, -69], [b'J2N3', 0, 11, -58], [b'BT-J6CWW3', 0, 11, -88],[b'BTWi-fi', 0, 11, -88]]
    user_display.display_networks( network_display )
    time.sleep(5)
    
    # test display only one network data entry
    network_display = [[b'J2N2', 0, 3, -67]]
    user_display.display_networks( network_display )
    time.sleep(5)
    
    # test display no network data
    network_display = [[]]
    user_display.display_networks( network_display )
    time.sleep(5)
