import obd
import time
import serial
from multiprocessing import Process, Queue
import sys
from functools import partial
import threading
from threading import Lock

PROGRAM_ALIVE = True
WORKER_ALIVE = True

INITIAL_RESTART_DELAY = 2
MAX_RESTART_DELAY = 8
STALL_TIMEOUT = 6
NULL_RESPONSE_TIMEOUT = 2

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
    cache_lock = Lock()
    try:
        baud = 38400
        ports = obd.scan_serial()

        if not ports:
            queue.put(("error", "no_ports"))
            return

        connection = obd.Async(
            portstr=ports[0],
            baudrate=baud,
            fast=False
        )

        if not connection.is_connected():
            queue.put(("error", "not_connected"))
            return

        availableCommands = connection.supported_commands
        commands = FilterCommands(
            CommandsToDictionary(availableCommands),
            "telemetry"
        )
        #print(commands)

        #Rolling cache
        for cmd, data in commands.items():
            OBDCACHE[cmd] = {
                "value": None,
                "command": data["command"],
                "prevValue": None, 
                "lastUpdate": None
            }

        for cmd, data in commands.items():
            callback_with_cache = partial(CacheCallback, OBDCACHE=OBDCACHE, lock=cache_lock)
            connection.watch(data["command"], callback=callback_with_cache)
        connection.start()
        while WORKER_ALIVE:
            time.sleep(1)
            changed = {}
            most_recent_update = 0

            with cache_lock:
                for cmd, data in OBDCACHE.items():
                    if data["lastUpdate"]:
                        if data["lastUpdate"] > most_recent_update:
                            most_recent_update = data["lastUpdate"]

                    if data["value"] != data["prevValue"]:
                        changed[cmd] = data

            if changed:
                queue.put(("data", changed, commands))
                for cmd in changed:
                    OBDCACHE[cmd]["prevValue"] = OBDCACHE[cmd]["value"]

            if most_recent_update and time.time() - most_recent_update > STALL_TIMEOUT:
                queue.put(("error", "TimeOut", None))
            

    except Exception as e:
        queue.put(("error", str(e), None))

    finally:
        try:
            connection.stop()
            connection.unwatch_all()
            connection.close() #close connection
        except:
            pass


# ==============================
# Supervisor
# ==============================
def wait_for_port():
    while True:
        ports = obd.scan_serial()
        if ports:
            return
        print("Waiting for emulator...")
        time.sleep(.25)


def StartWorker(queue):
    p = Process(target=OBDWorker, args=(queue,))
    p.start()
    return p


def Main():
    restart_delay = INITIAL_RESTART_DELAY
    queue = Queue()

    wait_for_port()
    worker = StartWorker(queue)

    last_heartbeat = time.time()
    restartTime = None
    CURRENT_CACHE = {}
    PREV_CACHE = {}

    try:
        while PROGRAM_ALIVE:
            time.sleep(1)

            # Process worker messages
            while not queue.empty():

                msg, data, cmds = queue.get()

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

            if(restartTime != None and time.time() >= restartTime):
                wait_for_port()
                worker = StartWorker(queue)

                restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
                last_heartbeat = time.time()
                restartTime = None

            for cmd, data in CURRENT_CACHE.items():
                print(str(data["command"].name) + " : " + data["value"] + " : " + str(data["lastUpdate"]))
    
    except KeyboardInterrupt:
        print("\nShutting down cleanly...")

    finally:
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


#Call main program
if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()   # Optional unless freezing, but safe
    Main()

