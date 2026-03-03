import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class PythonRunner {

    public static Process runPythonScript(String... args) throws IOException, InterruptedException {

        // Create temp working directory
        Path tempDir = Files.createTempDirectory("VehicleApp");
        System.out.println("Using temp directory: " + tempDir);

        // Extract Python script
        Path scriptPath = extractResource("/python/OBDCommModule.py", tempDir);

        // Extract requirements.txt
        Path requirementsPath = extractResource("/python/requirements.txt", tempDir);

        // Create venv inside temp dir
        Path venvPath = tempDir.resolve("venv");

        if (!Files.exists(venvPath)) {
            System.out.println("Creating Python virtual environment...");
            new ProcessBuilder("python", "-m", "venv", venvPath.toString())
                    .inheritIO()
                    .start()
                    .waitFor();
        }

        // Determine executables
        boolean isWindows = System.getProperty("os.name").toLowerCase().contains("win");

        String pipExecutable = isWindows
                ? venvPath.resolve("Scripts").resolve("pip.exe").toString()
                : venvPath.resolve("bin").resolve("pip").toString();

        String pythonExec = isWindows
                ? venvPath.resolve("Scripts").resolve("python.exe").toString()
                : venvPath.resolve("bin").resolve("python").toString();

        // Install dependencies
        System.out.println("Installing Python dependencies...");
        new ProcessBuilder(pipExecutable, "install", "-r", requirementsPath.toString())
                .inheritIO()
                .start()
                .waitFor();

        // Run Python script
        System.out.println("Starting Python script...");
        List<String> command = new ArrayList<>();
        command.add(pythonExec);
        command.add(scriptPath.toString());
        
        if (args != null) {
            Collections.addAll(command, args);
            }
        
        ProcessBuilder pbRun = new ProcessBuilder(command);
        pbRun.inheritIO();
        return pbRun.start();
    }

    private static Path extractResource(String resourcePath, Path outputDir) throws IOException {
        InputStream in = PythonRunner.class.getResourceAsStream(resourcePath);
        if (in == null) {
            throw new FileNotFoundException("Resource not found: " + resourcePath);
        }

        Path outputPath = outputDir.resolve(Paths.get(resourcePath).getFileName());
        Files.copy(in, outputPath, StandardCopyOption.REPLACE_EXISTING);
        return outputPath;
    }
}