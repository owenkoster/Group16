# User Manual

#### Description:
The system displays Diagnostic Trouble Codes to provide users with more information about failures detected by the user’s vehicle. It provides more information than a check engine light. These codes are generated automatically by the vehicle’s computer and can be read using the OBD-II port. It also provides the user with the vehicle’s state before the check engine light is triggered, the state when the light is triggered, and the state afterward allowing the user or a mechanic to properly diagnose and repair the root cause of the failure.This application will log the vehicle’s live sensor data and store it so the user or mechanic can find the root cause of the issue and properly repair it.

#### How to install the software:
##### Step 1:
Install Docker Desktop: https://www.docker.com/products/docker-desktop/
##### Step 2:
Install JDK25, or verify JDK version is greater than or equal to 25.0.2 by running "java -version" in the command line. 
Download link for JDK25: https://www.oracle.com/java/technologies/downloads/#jdk25-windows
##### Step 3:
Download the most recent version of OBD2GO from the releases tab.
Extract the ZIP file

#### How to run the software:
##### Step 0:
Ensure Docker Desktop is running
##### Step 1:
Open PowerShell or an equivalent command-line terminal
##### Step 2:
Navigate to where the project was extracted to, for example: "cd C:/MyFolder/"
##### Step 3:
Navigate into the subfolder elm327-docker
##### Step 4: 
Run the command: docker compose up --build
##### Step 5:
Open a new PowerShell or an equivalent command-line terminal
##### Step 6:
Navigate to where the project was extracted to, for example: "cd C:/MyFolder/"
##### Step 7:
Run the command: java -jar VehicleApp.jar
##### Step 8: 
Wait for the software to connect to the vehicle

#### To stop:
Ctrl+c in the terminal window, or the X button in the top right corner of the window. 

#### How to report a bug:
Please report bugs to GitHub issues. Please leave a detailed explanation of what the bug is: what was the actual behavior? vs. what was the expected behavior?

#### Known bugs:
None yet
