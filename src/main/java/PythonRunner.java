import java.io.File;
import java.io.IOException;

public class PythonRunner {

    // Run Python script with automatic requirements installation
    public static Process runPythonScript(String scriptPath) throws IOException, InterruptedException {
        // Step 1: Ensure virtual environment exists
        File venvDir = new File("venv");
        if (!venvDir.exists()) {
            System.out.println("Creating Python virtual environment...");
            ProcessBuilder pbVenv = new ProcessBuilder("python", "-m", "venv", "venv");
            pbVenv.inheritIO().start().waitFor();
        }

        // Step 2: Install requirements
        System.out.println("Installing Python dependencies...");
        String pipExecutable = System.getProperty("os.name").toLowerCase().contains("win") 
            ? "venv\\Scripts\\pip.exe"
            : "venv/bin/pip";

        ProcessBuilder pbInstall = new ProcessBuilder(pipExecutable, "install", "-r", "requirements.txt");
        pbInstall.inheritIO().start().waitFor();

        // Step 3: Run the Python script
        String pythonExec = System.getProperty("os.name").toLowerCase().contains("win")
            ? "venv\\Scripts\\python.exe"
            : "venv/bin/python";

        System.out.println("Starting Python script...");
        ProcessBuilder pbRun = new ProcessBuilder(pythonExec, scriptPath);
        pbRun.inheritIO(); // redirect Python output to Java console
        return pbRun.start();
    }
}