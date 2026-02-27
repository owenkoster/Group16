import obd
import time
import serial
from multiprocessing import Process, Queue
import sys
from functools import partial
import threading
from threading import Lock
import zmq
import json
import csv
import os
from datetime import datetime

#Program alive variables
PROGRAM_ALIVE = True
WORKER_ALIVE = True


INITIAL_RESTART_DELAY = 2
MAX_RESTART_DELAY = 8
STALL_TIMEOUT = 6
NULL_RESPONSE_TIMEOUT = 2
CURRENT_PORT = 0

# def CacheCallback(response, OBDCACHE, lock):
#     if response.is_null():
#         return
#     with lock:
#         OBDCACHE[response.command.name]["prevValue"] = OBDCACHE[response.command.name]["value"]
#         OBDCACHE[response.command.name]["lastUpdate"] = time.time()
#         OBDCACHE[response.command.name]["value"] = str(response.value)
def CacheCallback(response, OBDCACHE, lock):
    if response.is_null():
        return
    with lock:
        cmd_name = response.command.name
        OBDCACHE[cmd_name]["prevValue"] = OBDCACHE[cmd_name]["value"]
        OBDCACHE[cmd_name]["lastUpdate"] = time.time()
        
        if hasattr(response.value, 'magnitude'):
            OBDCACHE[cmd_name]["value"] = response.value.magnitude
            OBDCACHE[cmd_name]["unit"] = str(response.value.units)
        else:
            OBDCACHE[cmd_name]["value"] = str(response.value)
            OBDCACHE[cmd_name]["unit"] = "None"

# ==============================
# Worker Process
# ==============================
def OBDWorker(queue, currentPort):

    global WORKER_ALIVE
    global CURRENT_PORT

    OBDCACHE = {}
    
    cache_lock = Lock() #Cache update lock to prevent race conditions

    try:
        baud = 38400 #Set baud rate, this will eventually need to be done dynamically
        ports = obd.scan_serial() #scan for available ports
        if (CURRENT_PORT >= len(ports)):
            CURRENT_PORT = 0
        print("Current Port" + str(currentPort))
        print("TEST PORTS" + str(ports))
        if not ports:
            queue.put(("error", "no_ports"))
            return
        #connect to python obd
        connection = obd.Async(
            portstr=ports[currentPort],
            baudrate=baud,
            fast=False
        
        )

        #connection error
        if not connection.is_connected():
            queue.put(("error", "not_connected"))
            return

        #filter available commands
        availableCommands = connection.supported_commands
        commands = FilterCommands(
            CommandsToDictionary(availableCommands),
            ["telemetry","internal"]
        )


        #Local rolling cache initialization
        for cmd, data in commands.items():
            OBDCACHE[cmd] = {
                "value": "None",
                "command": data["command"], #keeps track of what the command was
                "unit" : "None",
                "prevValue": "None", 
                "lastUpdate": time.time()
            }
            #print(data["name"]) Testing print statement

        #Generate callbacks for each of the commands and tell pythonOBD to start watching them
        for cmd, data in commands.items():
            callback_with_cache = partial(CacheCallback, OBDCACHE=OBDCACHE, lock=cache_lock)
            connection.watch(data["command"], callback=callback_with_cache)
        
        connection.start() #start async monitoring
        
        #sends initial data through, allows for no update recorded to pass through
        with cache_lock: 
            queue.put(("data", OBDCACHE, commands))

        while WORKER_ALIVE:
            time.sleep(1)
            changed = {}
            most_recent_update = 0

            #This chunk of code updates the rolling cache,
            # and only sends data through up to the parent if the data changed.
            # Was done as a performance enhancement

            #lock the cache
            with cache_lock:
                for cmd, data in OBDCACHE.items():
                    #Find the most recent update, done for stall detection
                    if data["lastUpdate"]:
                        if data["lastUpdate"] > most_recent_update:
                            most_recent_update = data["lastUpdate"]
                    #check if the data was updated
                    if data["value"] != data["prevValue"]:
                        changed[cmd] = data

            #send updated data to the parent
            if changed:
                queue.put(("data", changed, commands))
                for cmd in changed:
                    OBDCACHE[cmd]["prevValue"] = OBDCACHE[cmd]["value"]
            #Detect stalls
            if most_recent_update and time.time() - most_recent_update > STALL_TIMEOUT:
                queue.put(("error", "TimeOut", None))
            

    except Exception as e:
        queue.put(("error", str(e), None))

    finally:
        try:
            #clean shutdown of the connection
            connection.stop()
            connection.unwatch_all()
            connection.close() #close connection
        except:
            pass


#Scan for available com ports
def wait_for_port():
    while True:
        ports = obd.scan_serial()
        #ports = ["/dev/ttys006"]
        if ports:
            return
        print("Waiting for emulator...")
        time.sleep(.25)

#helper function to start the worker process
def StartWorker(queue,currentPort):
    p = Process(target=OBDWorker, args=(queue,currentPort,))
    p.start()
    return p


class TripLogger:
    def __init__(self, log_dir="logs"):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Create filename: logs/trip_2025-02-18_16-30-00.csv
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filepath = os.path.join(log_dir, f"trip_{timestamp_str}.csv")
        
        self.file = open(self.filepath, mode='w', newline='', buffering=1)
        self.writer = csv.writer(self.file)
        
        # Write Header
        self.writer.writerow(["Timestamp_Unix", "PID", "Value", "Unit", "DTC_Codes"])
        print(f"[Logger] Recording trip to: {self.filepath}")

        # Log CSV
    def log(self, pid_name, value, unit, dtc_list=None):
        dtc_str = ";".join(dtc_list) if dtc_list else ""
        try:
            self.writer.writerow([time.time(), pid_name, value, unit, dtc_str])
            self.file.flush() 
        except Exception as e:
            print(f"[Logger Error] {e}")

    def close(self):
        if self.file:
            self.file.close()

def Main():
    queue = Queue()
    #context = zmq.Context() ZMQ communication already handled by zmq_publisher
    #socket = context.socket(zmq.PUB)
    #socket.bind("tcp://*:5555")
    logger = TripLogger()
    wait_for_port()
    currentPort = 0
    global CURRENT_PORT
    currentPort = 0
    worker = StartWorker(queue,currentPort)

    #initialize the childs heartbeat
    last_heartbeat = time.time()
    restartTime = None #Keeps track of when restart should be attempted
    restart_delay = INITIAL_RESTART_DELAY
    
    #Local current cache of the vehicle data
    CURRENT_CACHE = {}

    # Initialize ZeroMQ
    zmq_publisher = InitializeZMQ()

    # Start reply server for Java commands
    reply_thread = StartReplyServer()

    try:
        while PROGRAM_ALIVE:
            time.sleep(1)

            # Process worker messages
            while not queue.empty():

                msg, data, availableCommands = queue.get()

                #Good data sent
                if msg == "data":
                    #print("DATA AVAILABLE")
                    #print("-----------------------")
                    CURRENT_CACHE.update(data)
                    
                    for cmd_name, packet in data.items():
                        
                        if(time.time() - packet["lastUpdate"] <= NULL_RESPONSE_TIMEOUT):
                            last_heartbeat = time.time()
                            restart_delay = INITIAL_RESTART_DELAY

                        payload = {
                            "timestamp": packet["lastUpdate"] * 1000,
                            "pid": cmd_name,
                            "value": packet["value"],
                            "unit": packet.get("unit", ""),
                            "dtc": []
                        }
                        #socket.send_string(json.dumps(payload))

                        logger.log(cmd_name, packet["value"], packet.get("unit", ""))
                    # ---------------------------

                #Error with the child
                elif msg == "error":
                    print("Worker error: " + data)
                    restartTime = time.time() + restart_delay
                    worker.terminate()
                    worker.join()

                    print(f"Restarting in {restart_delay}s...")

            # Detect stall (blocked serial read protection)
            if time.time() - last_heartbeat > STALL_TIMEOUT and restartTime == None:
                print("Worker stalled. Killing.")
                restartTime = time.time() + restart_delay
                worker.terminate()
                worker.join()

                print(f"Restarting in {restart_delay}s...")
                #time.sleep(restart_delay)

            # Worker died unexpectedly
            if not worker.is_alive() and restartTime == None:
                print("Worker crashed.")

                print(f"Restarting in {restart_delay}s...")
                restartTime = time.time() + restart_delay

            #Worker process restart logic
            if(restartTime != None and time.time() >= restartTime):
                CURRENT_PORT += 1
                wait_for_port()
                worker = StartWorker(queue, CURRENT_PORT)

                restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
                last_heartbeat = time.time()
                restartTime = None
            #Removed testing print statements
            #elif(restartTime == None):
                #for cmd, data in CURRENT_CACHE.items(): #REPLACE ME
                #    print(str(data["command"].name) + " : " + str(data["value"]) + " : " + str(data["lastUpdate"])) #REPLACE ME
            
            #Use ZeroMQ function to publish data
            if(not CURRENT_CACHE):
                PublishVehicleData(zmq_publisher, {}) #Sends empty data if no data is available
            else:
                PublishVehicleData(zmq_publisher, CURRENT_CACHE) #We need to send cmds through because that is the list of available commands
    
    except KeyboardInterrupt:
        print("\nShutting down cleanly...")

    finally:
        # Cleanup ZeroMQ
        CleanupZMQ(zmq_publisher)

        worker.terminate()
        worker.join()
        logger.close()
        print("Supervisor exited.")

#filters the commands array to ignore any command not in the filtered categorys
def FilterCommands(commands, filters):

    filteredCommands = {}

    for name, data in commands.items():
        if (data['category'] in filters):
            filteredCommands[name] = data
    return filteredCommands

#Turns the set returned by pythonOBD into a dictionary of commands
def CommandsToDictionary(availableCommands):
    
    #Dictionary of available commands
    commands = {}
    
    #Loop through each available command
    for cmd in availableCommands:

        #Classify each command based on classification definitions
        if cmd.name in BLOCKED:
            category = "blocked"
        elif cmd.name in INTERNAL_ONLY:
            category = "internal"
        elif str(cmd.name).startswith(SYSTEM_PREFIXES):
            category = "on_demand"
        elif cmd.name in DISCOVERY:
            category = "on_demand"
        elif cmd.name in LOW_FREQ:
            category = "on_demand"
        else:
            category = "telemetry"

        #Build the dictionary entry
        commands[cmd.name] = {
            "name": cmd.name,
            "command": cmd,
            "description": cmd.desc,
            "category": category,
            "prevValue": None, 
            "lastUpdate": None
        }
    #Return the dictionary of commands
    return commands

#Prefix for DTC_ command. Should be normally ignored
SYSTEM_PREFIXES = ("DTC_",)

#Blocked commands that will never be run
BLOCKED = {
    "CLEAR_DTC", "GET_CURRENT_DTC",
}

# Commands for this scripts use only user should not use
INTERNAL_ONLY = {"GET_DTC", }

# Should only be run on command not constantly
DISCOVERY = {
    "PIDS_A", "PIDS_B", "PIDS_C", "PIDS_9A",
    "DTC_PIDS_B", "DTC_PIDS_C",
    "MIDS_A",
    "ELM_VERSION",
    "OBD_COMPLIANCE",
    "DTC_OBD_COMPLIANCE",
}

#Commands that are rarely run
LOW_FREQ = {
    "FUEL_TYPE",
    "FUEL_STATUS",
    "O2_SENSORS",
    "STATUS",
}

#ZMQ stuff

def InitializeZMQ(port=5555):

    """
    Initialize ZeroMQ publisher socket.

    Args:
        port: Port number to bind to (default: 5555)

    Returns:
        Dictionary containing context and publisher socket
    """

    try:
        context = zmq.Context()
        publisher = context.socket(zmq.PUB)
        publisher.bind(f"tcp://*:{port}")
        print(f"ZeroMQ Publisher initialized on port {port}")

        return {
            "context": context,
            "publisher": publisher,
            "enabled": True
        }

    except Exception as e:
        print(f"Failed to initialize ZeroMQ: {e}")
        return {
            "context": None,
            "publisher": None,
            "enabled": False
        }

def StartReplyServer():
    
    """
    Start a Reply server in a separate thread to handle Java requests/commands
    """

    def reply_worker():
        global PROGRAM_ALIVE

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5556") # Different port than publisher
        print("ZeroMQ Reply server started on port 5556")

        while PROGRAM_ALIVE:
            try:
                # Set timeout so we can check PROGRAM_ALIVE preiodically
                socket.setsockopt(zmq.RCVTIMEO, 1000) # 1 second timeout

                # Wait for request from Java
                request = socket.recv_string()
                print(f"Received command from Java: {request}")

                # Process request
                if request == "SHUTDOWN":
                    PROGRAM_ALIVE = False
                    response = {"status": "ok", "message": "Shutting down..."}
                    socket.send_string(json.dumps(response))
                    print("Shutdown command received from Java")
                    break

                elif request == "PING":
                    response = {"status": "ok", "message": "Python is alive"}
                    socket.send_string(json.dumps(response))

                elif request == "STATUS":
                    response = {"status": "ok", "connected": True, "uptime": time.time()}
                    socket.send_string(json.dumps(response))

                else:
                    response = {"status": "error", "message": "Unknown command"}
                    socket.send_string(json.dumps(response))

            except zmq.Again:
                # Timeout - no message received, loop continues
                continue
            except Exception as e:
                print(f"Reply server error: {e}")
                break

        socket.close()
        context.term()
        print("Reply server shut down")

    # Start in background thread
    thread = threading.Thread(target=reply_worker, daemon=True)
    thread.start()
    return thread


def PublishVehicleData(zmq_publisher, cache_data):

    """
    Publish vehicle data over ZeroMQ.

    Args:
        zmq_publisher: Dictionary containing ZeroMQ publisher info
        cache_data: Current vehicle data cache (CURRENT_CACHE)
    """

    if not zmq_publisher or not zmq_publisher.get("enabled"):
        return
    
    try:
        # Prepare data for transmission
        vehicle_data = {
            "timestamp": time.time(),
            "data": {}
        }

        # Convert cache data to JSON-serializable format
        for cmd, data in cache_data.items():
            vehicle_data["data"][cmd] = {
                "value": data["value"],
                "unit": data["unit"],
                "lastUpdate": data["lastUpdate"]
            }

        # Publish only if there's data
        # Test to send empty data to notify UI of no connection 
        #if vehicle_data["data"]:
        message = json.dumps(vehicle_data)
        zmq_publisher["publisher"].send_string(f"VEHICLE_DATA {message}")
            #debug:
            #print(f"Published {len(vehicle_data['data'])} values via ZeroMQ")

    except Exception as e:
        print(f"Error publishing to ZeroMQ: {e}")

def CleanupZMQ(zmq_publisher):
    
    """
    Cleanup ZeroMQ resources.

    Args:
        zmq_publisher: Dictionary containing ZeroMQ publisher info
    """

    if not zmq_publisher or not zmq_publisher.get("enabled"):
        return

    try:
        print("Shutting down ZeroMQ...")
        if zmq_publisher["publisher"]:
            zmq_publisher["publisher"].close()
        if zmq_publisher["context"]:
            zmq_publisher["context"].term()
        print("ZeroMQ shutdown complete.")
    except Exception as e:
        print(f"Error during ZeroMQ cleanup: {e}")

#Call main program
if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()   # Optional unless freezing, but safe
    Main()

