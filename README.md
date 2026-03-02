# A new way to monitor your vehicle, OBD-2GO! (subject to change) - Team 16
### 1. Team info:
Owen Koster,
Peyton DuPont
Tiernan Flanagan-Caldwell
Silas Jones
   
   The main method of communication is Discord
   
### 2. Product description

A notorious source of headache for drivers has always been the dreaded check engine light. When it comes on, it leaves you with the anxiety of knowing something might be terribly wrong with your vehicle – Or it could be nothing. The OBD-2GO aims to make this system more transparent so drivers don’t have to worry about what might be wrong with their vehicle. The OBD-2GO will be a system embedded into your vehicle that will actively monitor and warn you of issues with your vehicle in a more detailed manner than a simple check engine light. It will also enable you to monitor and record vehicle parameters while driving, so that you can know what shows signs of failure before the problem becomes much more expensive.

### 3. How to run the software

#### How to install the software:
##### Step 1:
Open PowerShell or an equivalent command-line terminal
##### Step 2:
Install JDK25, or verify JDK version is greater than or equal to 25.0.2 by running "java -version" in the command line. 
Download link for JDK25: https://www.oracle.com/java/technologies/downloads/#jdk25-windows
##### Step 3:
Download the most recent version of the software from the releases tab.
Extract the ZIP file

#### How to run the software:
##### Step 1:
Open PowerShell or an equivalent command-line terminal
##### Step 2:
Navigate to where the project was extracted to, for example: "cd C:/MyFolder/"
##### Step 3:
Run the command: java -jar VehicleApp.jar
##### Step 4: 
Wait for the software to connect to the vehicle

#### How to install the emulator to test the software:
##### Step 1: 
Download the most recent version of Python. On windows get it from the Microsoft Store
##### Step 2:
Open PowerShell or an equivalent command-line terminal
##### Step 3:
Run the commands:
 - pip install pyyaml
 - pip install python-daemon
 - pip install obd
##### Step 4:
On a Windows machine, the emulator requires com0com to simulate a COM port. 
Download: https://sourceforge.net/projects/com0com/ 
Follow the installation instructions for com0com
Next, open Device Manager, click on: com0com - serial port emulators
Right-click on one of the COM ports in the drop-down and click Update Driver
next click search automatically, then click search on Windows Update
Inside the Windows Update menu in settings, click Advanced options, then press Optional updates, and install the update for com0com
Restart the computer
next in the Windows search bar, type setup and run the setup program. This will require .net
Set up a Virtual port pair, the only options that should be ticked are emulate baud rate and enable buffer overrun
One port must be named COM3, and the other can be named COM#, where # is any number from 1-9, not including 3
Click apply
##### Step 5:
finally download the latest release of the emulator from: https://github.com/Ircama/ELM327-emulator 
Unzip the folder and double-click the .exe
Once the emulator terminal is open, type in scenario to switch the mode to car
##### Step 6:
The emulator is ready to be used to test the software
### 4. Use cases functional

