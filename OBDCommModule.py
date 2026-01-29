import obd
import time
import os

# Specify the port the emulator is connected to (e.g., COM5 on Windows)
# For Linux/macOS, it might be a path like '/dev/ttyUSB0' or similar
c = obd.Async("COM6", baudrate=38400) #2 for emulator.
#still need to figure out automatic port sensing

# Wait for the connection to establish
time.sleep(3) 

if c.is_connected():
    print("Connected to the ELM327 emulator!")
    
    commandsAvailable = c.supported_commands
    print("Supported:", commandsAvailable)
    print("\n\n")
    #for ii in range(0, 20):
    #    print(commandsAvailable[ii])
    #command = obd.commands.CLEAR_DTC 
    #response = c.query(command)

    c.watch(obd.commands.GET_DTC);
    c.watch(obd.commands.SHORT_FUEL_TRIM_1)
    c.watch(obd.commands.SHORT_FUEL_TRIM_2)
    c.watch(obd.commands.RPM)
    c.watch(obd.commands.SPEED)
    c.watch(obd.commands.COOLANT_TEMP)
    c.start() # start the async update loop
    while(True):
        print(c.query(obd.commands.GET_DTC))
        print(c.query(obd.commands.RPM))
        print(c.query(obd.commands.SPEED))
        print(c.query(obd.commands.COOLANT_TEMP))
        print(c.query(obd.commands.SHORT_FUEL_TRIM_1))
        print(c.query(obd.commands.SHORT_FUEL_TRIM_2))
        time.sleep(.8)

    # Query for Engine RPM (example command)
    #command = obd.commands.RPM 
    #response = connection.query(command) #
    #print(f"Engine RPM: {response.value}") # response.value provides the parsed data
    
    # You can query other data points as well, e.g., Vehicle Speed (SPEED)
    #command_speed = obd.commands.SPEED
    #response_speed = connection.query(command_speed)
    #print(f"Vehicle Speed: {response_speed.value}")
    
    #command_coolantTemp = obd.commands.COOLANT_TEMP
    #response_coolantTemp = connection.query(command_coolantTemp)
    #print(f"Vehicle Speed: {response_coolantTemp.value}")


    # Close the connection
    c.close()
else:
    print("Failed to connect to the emulator.")