# A new way to monitor your vehicle, OBD-2GO! - Team 16
### 1. Team info:
Owen Koster,
Peyton DuPont
Tiernan Flanagan-Caldwell
Silas Jones

### 2. Product description

A notorious source of headache for drivers has always been the dreaded check engine light. When it comes on, it leaves you with the anxiety of knowing something might be terribly wrong with your vehicle – Or it could be nothing. The OBD-2GO aims to make this system more transparent so drivers don’t have to worry about what might be wrong with their vehicle. The OBD-2GO will be a system embedded into your vehicle that will actively monitor and warn you of issues with your vehicle in a more detailed manner than a simple check engine light. It will also enable you to monitor and record vehicle parameters while driving, so that you can know what shows signs of failure before the problem becomes much more expensive. Also supports exporting and importing logs of your drives to help pinpoint your issues.


### 3. Use cases functional
Currently, the user can view all available sensor data in standard mode. The user can also read any trouble codes found while in driving mode and can view a graph of the current vehicle speed. The log system works and will output CSV files with logged vehicle data into the logs folder in the same directory as the .jar file. The user can freely switch between driving mode and standard mode. 

### 4. How install and run the software

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
Ensure docker desktop is running
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
