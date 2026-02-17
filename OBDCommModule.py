import obd
import time
import serial
from multiprocessing import Process, Queue
import sys

PROGRAM_ALIVE = True
WORKER_ALIVE = True

INITIAL_RESTART_DELAY = 2
MAX_RESTART_DELAY = 8
STALL_TIMEOUT = 8

# ==============================
# Worker Process
# ==============================
def OBDWorker(queue):
    global WORKER_ALIVE
    try:
        baud = 38400
        ports = obd.scan_serial()

        if not ports:
            queue.put(("error", "no_ports"))
            return

        connection = obd.OBD(
            portstr=ports[0],
            baudrate=baud,
            timeout=0.5,
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
        #placeholder for live cache
        rpm_cmd = commands["RPM"]["command"]

        while WORKER_ALIVE:
            response = connection.query(rpm_cmd)

            if response.is_null():
                queue.put(("error", "null_response"))
                break

            rpm = response.value
            queue.put(("data", rpm))

            time.sleep(1)
        # End placeholder

    except Exception as e:
        queue.put(("error", str(e)))

    finally:
        try:
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
        time.sleep(1)


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

    while PROGRAM_ALIVE:
        time.sleep(1)

        # Process worker messages
        while not queue.empty():
            msg_type, data = queue.get()

            if msg_type == "data":
                print("Supervisor: Connection Healthy")
                print("Response", data)
                last_heartbeat = time.time()
                restart_delay = INITIAL_RESTART_DELAY

            elif msg_type == "error":
                print("Worker error:", data)
                worker.terminate()
                worker.join()

                print(f"Restarting in {restart_delay}s...")
                time.sleep(restart_delay)

                wait_for_port()
                worker = StartWorker(queue)

                restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
                last_heartbeat = time.time()

        # Detect stall (blocked serial read protection)
        if time.time() - last_heartbeat > STALL_TIMEOUT:
            print("Worker stalled. Killing.")
            worker.terminate()
            worker.join()

            print(f"Restarting in {restart_delay}s...")
            time.sleep(restart_delay)

            wait_for_port()
            worker = StartWorker(queue)

            restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
            last_heartbeat = time.time()

        # Worker died unexpectedly
        if not worker.is_alive():
            print("Worker crashed.")

            print(f"Restarting in {restart_delay}s...")
            time.sleep(restart_delay)

            wait_for_port()
            worker = StartWorker(queue)

            restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
            last_heartbeat = time.time()

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

#Call main program
if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()   # Optional unless freezing, but safe
    Main()