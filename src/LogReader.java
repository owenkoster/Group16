import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class LogReader {

    public static class LogEntry {
        public double timestamp;
        public String pid;
        public double value;
        public String unit;
        public String[] dtcCodes;

        public LogEntry(double t, String p, double v, String u, String[] d) {
            this.timestamp = t;
            this.pid = p;
            this.value = v;
            this.unit = u;
            this.dtcCodes = d;
        }
    }

    public List<LogEntry> readLogFile(File file) {
        List<LogEntry> entries = new ArrayList<>();
        String line = "";
        String delimiter = ",";

        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            if ((line = br.readLine()) == null) {
                return entries;
            }

            while ((line = br.readLine()) != null) {
                String[] data = line.split(delimiter, -1);

                try {
                    // CSV Columns: [0]Timestamp, [1]PID, [2]Value, [3]Unit, [4]DTC
                    double timestamp = Double.parseDouble(data[0]);
                    String pid = data[1];
                    double value = Double.parseDouble(data[2]);
                    String unit = data[3];
                    
                    String[] dtcs = new String[0];
                    if (data.length > 4 && !data[4].isEmpty()) {
                        dtcs = data[4].split(";");
                    }

                    entries.add(new LogEntry(timestamp, pid, value, unit, dtcs));

                } catch (NumberFormatException e) {
                    System.err.println("Skipping corrupt line: " + line);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        return entries;
    }
}