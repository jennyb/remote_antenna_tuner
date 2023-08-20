import json
# This class restores and saves the current stepper motor positions to program memory as a file
# The Pi Pico does not have any non volitile RAM ( RAM that survives power off/reboot ) so we are forced
# to use Program Flash memory that uses a block read/erase/write to store data - 100,000 erase cycles before
# the program memory is worn. Luckily AFAIK the Micropython kernel handles this as presents a file interface
# doing all the work including the wear protection.
#
# On initialise the xyzzy.txt file is loaded into RAM containing the current stepper motor locations and memoried
# locations ( number of steps )
# The class also handles saving to files for the stepper positions and memories
class Storage:
    def __init__(self, file:str ):
        try:
            with open(file) as fd:
                self.config = json.load(fd)
                self.steppers = self.config["stepper_stored_pos"]
                self.memories = self.config["memory"]
                self.ssid = self.config["ssid"]
                self.password = self.config["password"]
                fd.close()
                
        #If there is no file, create one containing these defaults   
        except OSError:
            print(f'Storage file {file} not found, creating a new storage file')
            with open(file, "w") as fd:
                tmp_stepper_pos = [0,0,0]
                tmp_create_memories = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],]
                self.config = {
                    "stepper_stored_pos": tmp_stepper_pos,
                    "memory": tmp_create_memories,
                    "ssid": "default",
                    "password": "default",
                }
                json.dump(self.config, fd)
                fd.close()

    def write_memory( self, file:str,  memory_number:int, mem_steppers):
        with open(file, "w") as fd:
            self.config['memory'][memory_number] = mem_steppers
            json.dump(self.config, fd)
            fd.close() 
    
    def write_current_steppers( self, file:str, current_steps):
        with open(file, "w") as fd:
            self.config["stepper_stored_pos"] = current_steps
            json.dump(self.config, fd)
            fd.close()         

    def get_stepper_positions(self):
        return self.config["stepper_stored_pos"] 

    def get_memory(self, memory_number:str):
        return self.config['memory'][memory_number]
    
    def get_ssid( self ):
        return self.config["ssid"]
    
    def get_password( self ):
        return self.config["password"]
 
if __name__ == '__main__':
    # test data :
    # fill the memory space for 5 bands, high and low settings for each 

    test_positions1 = [16,250,8]
    test_positions2 = [1,100,32]    
    file = 'test.txt'
    nv_data = Storage(file)    
 
    print( f'current stepper positions: {nv_data.get_stepper_positions()}\n')
    nv_data.write_current_steppers( file, test_positions1 )
    print( f'current stepper positions: {nv_data.get_stepper_positions()}\n')
    
    nv_data.write_memory(file, 3,test_positions1)
    print( f'memory 3: {nv_data.get_memory(3)}\n')
    
    nv_data.write_memory(file, 3,test_positions2)
    print( f'memory 3: {nv_data.get_memory(3)}\n')
    
    # We don't need to set the password. The user can change the file on the pico to suit their network
    print( f'SSID: {nv_data.get_ssid()}')
    


    