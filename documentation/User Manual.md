# User Manual

#### Description:
The system displays Diagnostic Trouble Codes to provide users with more information about failures detected by the user’s vehicle. It provides more information than a check engine light. These codes are generated automatically by the vehicle’s computer and can be read using the OBD-II port. It also provides the user with the vehicle’s state before the check engine light is triggered, the state when the light is triggered, and the state afterward allowing the user or a mechanic to properly diagnose and repair the root cause of the failure.This application will log the vehicle’s live sensor data and store it so the user or mechanic can find the root cause of the issue and properly repair it.

#### How to install the software:
Step 1:
Open PowerShell or an equivalent command-line terminal
Step 2:
Install JDK25, or verify JDK version is greater than or equal to 25.0.2 by running "java -version" in the command line. 
Download link for JDK25: https://www.oracle.com/java/technologies/downloads/#jdk25-windows
Step 3:
Download the most recent version of the software from the releases tab.
Extract the ZIP file

#### How to run the software:
Step 1:
Open PowerShell or an equivalent command-line terminal
Step 2:
Navigate to where the project was extracted to, Example: "cd C:/MyFolder/"
Step 3:
Run the command: java -jar VehicleApp.jar
Step 4: 
Wait for the software to connect to the vehicle

#### How to install the emulator to test the software:
Step 1: 
Download the most recent version of Python. On windows get it from the Microsoft Store
Step 2:
Open PowerShell or an equivalent command-line terminal
Step 3:
run the commands:
pip install pyyaml
pip install python-daemon
pip install obd
Step 4:
On a windows machine the emulator requires com0com to simulate a com port. 
Download: https://sourceforge.net/projects/com0com/ 
Follow the installation instructions for com0com
Next, open Device Manager, click on: com0com - serial port emulators
right click on one of the com ports in the drop down and click Update Driver
next click search automatically, then click search on Windows Update
Inside the Windows Update menu in settings, click Advanced options, then press Optional updates, and install the update for com0com
Restart the computer
next in the windows search bar type setup and run the program
Set up a Virtual port pair, the only options that should be ticked are emulate baud rate and enable buffer overrun
One port must be named COM3, and the other can be named COM#, where # is any number from 1-9, not including 3
Click apply
Step 5:
finally download the latest release of the emulator from: https://github.com/Ircama/ELM327-emulator 
Unzip the folder and double click the .exe
Once the emulator terminal is open, type in scenario to switch the mode to car
Step 6:
Emulator is ready to be used to test the software


To stop:
Ctrl+c in the terminal window, or the X button in the top right corner of the window. 

#### How to report a bug:
Please report bugs to GitHub issues. Please leave a detailed explanation of what the bug is: what was the actual behavior? vs. what was the expected behavior?

#### Known bugs:
None yet
