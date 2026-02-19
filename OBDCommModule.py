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

#Program alive variables
PROGRAM_ALIVE = True
WORKER_ALIVE = True


INITIAL_RESTART_DELAY = 2
MAX_RESTART_DELAY = 8
STALL_TIMEOUT = 6
NULL_RESPONSE_TIMEOUT = 2

#callback function to update the rolling cache
def CacheCallback(response, OBDCACHE, lock):
    if response.is_null():
        return
    with lock:
        OBDCACHE[response.command.name]["prevValue"] = OBDCACHE[response.command.name]["value"]
        OBDCACHE[response.command.name]["lastUpdate"] = time.time()
        OBDCACHE[response.command.name]["value"] = str(response.value)


# ==============================
# Worker Process
# ==============================
def OBDWorker(queue):

    global WORKER_ALIVE
    
    OBDCACHE = {}
    
    cache_lock = Lock() #Cache update lock to prevent race conditions

    try:
        baud = 38400 #Set baud rate, this will eventually need to be done dynamically
        ports = obd.scan_serial() #scan for available ports

        if not ports:
            queue.put(("error", "no_ports"))
            return

        #connect to python obd
        connection = obd.Async(
            portstr=ports[0],
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
            "telemetry"
        )
        #print(commands)

        #Local rolling cache initialization
        for cmd, data in commands.items():
            OBDCACHE[cmd] = {
                "value": None,
                "command": data["command"], #keeps track of what the command was
                "prevValue": None, 
                "lastUpdate": None
            }

        #Generate callbacks for each of the commands and tell pythonOBD to start watching them
        for cmd, data in commands.items():
            callback_with_cache = partial(CacheCallback, OBDCACHE=OBDCACHE, lock=cache_lock)
            connection.watch(data["command"], callback=callback_with_cache)
        
        connection.start() #start async monitoring
        
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
        if ports:
            return
        print("Waiting for emulator...")
        time.sleep(.25)

#helper function to start the worker process
def StartWorker(queue):
    p = Process(target=OBDWorker, args=(queue,))
    p.start()
    return p


def Main():

    restart_delay = INITIAL_RESTART_DELAY #delay for restarting the child after a disconnect
    queue = Queue() #initialize the queue

    wait_for_port() #scan for available com ports
    worker = StartWorker(queue) #initialize the child

    #initialize the childs heartbeat
    last_heartbeat = time.time()
    restartTime = None #Keeps track of when restart should be attempted
    
    #Local current and previous caches for the vehicle data
    CURRENT_CACHE = {}
    PREV_CACHE = {}

    # Initialize ZeroMQ
    zmq_publisher = InitializeZMQ()

    try:
        while PROGRAM_ALIVE:
            time.sleep(1)

            # Process worker messages
            while not queue.empty():

                msg, data, availableCommands = queue.get()

                #Good data sent
                if msg == "data":
                    print("Supervisor: Connection Healthy")
                    print("------------------------------")
                    PREV_CACHE = CURRENT_CACHE.copy()
                    CURRENT_CACHE.update(data)
                    for key, value in CURRENT_CACHE.items():
                        if(time.time() - value["lastUpdate"] <= NULL_RESPONSE_TIMEOUT):
                            last_heartbeat = time.time()
                            restart_delay = INITIAL_RESTART_DELAY
                            break

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
                wait_for_port()
                worker = StartWorker(queue)

                restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
                last_heartbeat = time.time()
                restartTime = None

            #Use ZeroMQ function to publish data
            PublishVehicleData(zmq_publisher, CURRENT_CACHE) #We need to send cmds through because that is the list of available commands

            for cmd, data in CURRENT_CACHE.items(): #REPLACE ME
                print(str(data["command"].name) + " : " + data["value"] + " : " + str(data["lastUpdate"])) #REPLACE ME
    
    except KeyboardInterrupt:
        print("\nShutting down cleanly...")

    finally:
        # Cleanup ZeroMQ
        CleanupZMQ(zmq_publisher)

        worker.terminate()
        worker.join()
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
    "CLEAR_DTC",
}

# Commands for this scripts use only user should not use
INTERNAL_ONLY = {"GET_DTC", "GET_CURRENT_DTC"}

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
                "lastUpdate": data["lastUpdate"]
            }

        # Publish only if there's data
        if vehicle_data["data"]:
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

