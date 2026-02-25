import java.util.Map;

import org.zeromq.ZContext;
import org.zeromq.ZMQ;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

public class VehicleDataReceiver {

    private static void sendShutdownCommand() {
      try (ZContext context = new ZContext()) {
        ZMQ.Socket requester = context.createSocket(ZMQ.REQ);
        requester.connect("tcp://localhost:5556");

        // Set timeout to avoid hanging
        requester.setReceiveTimeOut(2000); // 2 second timeout

        // Send shutdown command
        System.out.println("Sending shutdown command to Python...");
        requeseter.send("SHUTDOWN".getBytes(ZMQ.CHARSET), 0);

        // Wait for acknowledgment
        String reply = requester.recvStr(0);
        if (reply != null) {
          System.out.println("Python response: " + reply);
        }

      } catch (Excpetion e) {
        System.out.println("Could not send shutdown command: " + e.getMessage());

      }
    }
    
    public static void initDataReceiver() {
        // Create ZeroMQ context and subscriber socket
        try (ZContext context = new ZContext()) {
            ZMQ.Socket subscriber = context.createSocket(ZMQ.SUB);
            
            // Connect to the Python publisher
            String pythonHost = "tcp://localhost:5555";  // Change if Python runs on different machine
            subscriber.connect(pythonHost);
            
            // Subscribe to all messages starting with "VEHICLE_DATA"
            subscriber.subscribe("VEHICLE_DATA".getBytes(ZMQ.CHARSET));
            
            System.out.println("Connected to Python OBD publisher at " + pythonHost);
            System.out.println("Waiting for vehicle data...\n");
            
            Gson gson = new Gson();
            
            // Receive loop
            while (!Thread.currentThread().isInterrupted()) {
                // Receive message
                String message = subscriber.recvStr(0);
                
                if (message != null) {
                    // Remove the topic prefix "VEHICLE_DATA "
                    String jsonData = message.substring("VEHICLE_DATA ".length());
                    
                    // Parse JSON
                    JsonObject vehicleData = gson.fromJson(jsonData, JsonObject.class);
                    
                    // Extract timestamp
                    double timestamp = vehicleData.get("timestamp").getAsDouble();
                    
                    // Extract data object
                    JsonObject data = vehicleData.getAsJsonObject("data");
                    
                    // Display data
                    System.out.println("========== Vehicle Data ==========");
                    System.out.println("Timestamp: " + timestamp);
                    System.out.println("----------------------------------");
                    
                    // Iterate through all vehicle parameters
                    for (Map.Entry<String, JsonElement> entry : data.entrySet()) {
                        String commandName = entry.getKey();
                        JsonObject commandData = entry.getValue().getAsJsonObject();
                        
                        String value = commandData.get("value").getAsString();
                        double lastUpdate = commandData.get("lastUpdate").getAsDouble();
                        
                        System.out.println(commandName + ": " + value + 
                                         " (updated: " + lastUpdate + ")");
                    }
                    System.out.println("==================================\n");
                    
                    // Process specific values (example)
                    processVehicleData(data);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
          // Ensure shutdown is sent even on error
          sendShutdownCommand();
    }
    
    /**
     * Process vehicle data for specific conditions or alerts
     */
    private static void processVehicleData(JsonObject data) {
        // Example: Check RPM
        if (data.has("RPM")) {
            JsonObject rpmData = data.getAsJsonObject("RPM");
            String rpmValue = rpmData.get("value").getAsString();
            
            // Extract numeric value (assuming format like "3500.0 revolutions_per_minute")
            try {
                String numericPart = rpmValue.split(" ")[0];
                double rpm = Double.parseDouble(numericPart);
                
                if (rpm > 5000) {
                    System.out.println("WARNING: High RPM detected: " + rpm);
                }
            } catch (Exception e) {
                // Handle parsing errors
            }
        }
        
        // Example: Check Speed
        if (data.has("SPEED")) {
            JsonObject speedData = data.getAsJsonObject("SPEED");
            String speedValue = speedData.get("value").getAsString();
            
            try {
                String numericPart = speedValue.split(" ")[0];
                double speed = Double.parseDouble(numericPart);
                
                if (speed > 120) {
                    System.out.println("WARNING: High speed detected: " + speed);
                }
            } catch (Exception e) {
                // Handle parsing errors
            }
        }
        
        // Example: Check Coolant Temperature
        if (data.has("COOLANT_TEMP")) {
            JsonObject tempData = data.getAsJsonObject("COOLANT_TEMP");
            String tempValue = tempData.get("value").getAsString();
            
            try {
                String numericPart = tempValue.split(" ")[0];
                double temp = Double.parseDouble(numericPart);
                
                if (temp > 100) {
                    System.out.println("ALERT: Engine overheating! Temp: " + temp + "degrees C");
                }
            } catch (Exception e) {
                // Handle parsing errors
            }
        }
    }
}
