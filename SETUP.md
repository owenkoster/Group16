#### How to obtain the source code:
- Can be downloaded directly from GitHub
#### Install Docker Desktop:
Install Docker Desktop: https://www.docker.com/products/docker-desktop/
##### Install or verify JDK25:
Install JDK25, or verify JDK version is greater than or equal to 25.0.2 by running "java -version" in the command line. 
Download link for JDK25: https://www.oracle.com/java/technologies/downloads/#jdk25-windows
#### Install Maven:
Install Maven: https://maven.apache.org/download.cgi
#### How to build the software:
 - The code is automatically built and tested when it is pushed to GitHub
 - To build and run the software locally using Maven, run the commands below in the terminal
##### Commands:
 - mvn clean package
 - java -jar target/VehicleApp.jar -- Runs the program
 - docker compose build -- Builds the docker (run this in the elm32-docker directory)
#### How to build a release of the software:
 - Releases are made by putting the Docker container from the source code into a folder named "OBD2GO". Then, take the most recent GitHub Actions build and put it in the main folder. Compress the main folder into a zip file. Next, create a new release.
