# Developer Guidelines

#### How to obtain the source code:
- Can be downloaded directly from GitHub

#### Layout of directory structure:
- The documentation directory contains the user documentation and developer guidelines
- The lib directory contains the dependencies needed for the code to be able to run.
- The log directory contains logs from user’s drives in .csv format.
- The reports directory contains our group’s reports as we make progress throughout the term.
- The src directory contains the java files that make up the UI.
- The OBDCommModule.py file is the main python file that communicates with the vehicle’s OBD.
- The Project Living Document.pdf is our project’s living document.
- The README.md file contains a short description of our project.
- The elm-327 docker directory contains the files that make the docker for our project work properly.
- The tests directory contain our written tests.

#### How to build the software:
 - The code is automatically built and tested when it is pushed to GitHub
 - To build and run the software locally using Maven, run the commands below in the terminal
#####
 - mvn clean package
 - java -jar target/VehicleApp.jar

#### How to test the software:
 - Unit tests are run automatically when code is pushed to GitHub. Tests can be run manually by going to the GitHub actions tab, clicking on one of the workflow runs, and pressing rerun all tests. 

#### How to add new tests:
 - Add new Java tests to the folder in src/test/java. Follow the format of the sample test.
 - Add new Python tests to the /tests/ folder. Make sure the names of the new tests start with test_. This is important because we use pytest, and for the tests to run automatically, they must start with test_

#### How to build a release of the software:
 - Releases are made by putting the Docker container from the source code into a folder named "OBD2GO". Then, take the most recent GitHub Actions build and put it in the main folder. Compress the main folder into a zip file. Next, create a new release.
