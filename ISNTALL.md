### How to install the software:
##### Step 1:
Install Docker Desktop: https://www.docker.com/products/docker-desktop/
##### Step 2:
Install JDK25, or verify JDK version is greater than or equal to 25.0.2 by running "java -version" in the command line. 
Download link for JDK25: https://www.oracle.com/java/technologies/downloads/#jdk25-windows
##### Step 3:
Download the most recent version of OBD2GO from the releases tab.
Extract the ZIP file

#### How to run the software:
##### Note
If you are connecting to a vehicle through the OBD2 port, skip to step 5
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
