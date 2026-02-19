# User Manual

#### Description:
The system displays Diagnostic Trouble Codes to provide users with more information about failures detected by the user’s vehicle. It provides more information than a check engine light. These codes are generated automatically by the vehicle’s computer and can be read using the OBD-II port. It also provides the user with the vehicle’s state before the check engine light is triggered, the state when the light is triggered, and the state afterward allowing the user or a mechanic to properly diagnose and repair the root cause of the failure.This application will log the vehicle’s live sensor data and store it so the user or mechanic can find the root cause of the issue and properly repair it.

#### How to install the software:
Work in progress

#### How to run the software:
Step 1:
pip install pyzmq
pip install obd
Here's a link to the Python OBD documentaion for extra help: https://python-obd.readthedocs.io/en/latest/

Step 2:
In your terminal in the main directory (Group16), to compile the java code write:
$ javac -cp “lib/jeromq-0.5.3.jar;lib/gson-2.10.1.jar” VehicleDataReceiver.java

Step 3:

Open your first command prompt and run the java file:
Java -cp “.;lib/jeromq-0.5.3.jar:lib/gson-2.10.1.jar” VehicleDataReceiver

Then wait for the message:
“ZeroMQ Publisher initialized on port 5555”

Step 4 (Final Step):
Open a second command prompt and run the python file:
$ python OBDCommModule.py

To stop:
Ctrl+c in each window

#### How to report a bug:
Please report bugs to GitHub issues. Please leave a detailed explanation of what the bug is: what was the actual behavior? vs. what was the expected behavior?

#### Known bugs:
None yet
