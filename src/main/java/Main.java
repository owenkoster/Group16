import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

public class Main {

    static JFrame window;

    static JPanel MainPanel;
    static JPanel DrivingMode;
    static JPanel StandardMode;

    public static void setDrivingMode(boolean drivingMode) {
        DrivingMode.setVisible(drivingMode);
        StandardMode.setVisible(!drivingMode);
    }

    public static void main(String[] args) {
        Process pythonProcess;
        try {
            // Launch Python script
            pythonProcess = PythonRunner.runPythonScript("src/main/python/OBDCommModule.py");

            // Java continues to run (you can communicate over ZeroMQ)
            // Wait for Python to finish if desired:
            // pythonProcess.waitFor();

        } catch (Exception e) {
            e.printStackTrace();
            return;
        }

        //style
        try {
            for (UIManager.LookAndFeelInfo info : UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    UIManager.setLookAndFeel(info.getClassName());
                    System.out.println("Set look and feel to "+info.getName());
                    break;
                }
            }
        } catch (Exception ignored) {}

        //window
        window = new JFrame();
        window.setTitle("OBD-2GO!");
        window.setDefaultCloseOperation(JFrame.DO_NOTHING_ON_CLOSE);
        window.setSize(800,500);
        window.setLocationRelativeTo(null);
        window.addWindowListener(new WindowAdapter() {
            @Override
            public void windowClosing(WindowEvent e) {
                int response = JOptionPane.showConfirmDialog(window, "Are you sure you want to exit?",
                        "Confirm Exit", JOptionPane.YES_NO_OPTION);
                if (response == JOptionPane.YES_OPTION) {
                    pythonProcess.destroy();
                    System.exit(0);
                }
            }
        });

        //mode swapping buttons
        JButton DrivingModeButton = new JButton("Driving Mode");
        DrivingModeButton.setFont(Util.SMALL_FONT);
        DrivingModeButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                setDrivingMode(true);
            }
        });
        JButton StandardModeButton = new JButton("Standard Mode");
        StandardModeButton.setFont(Util.SMALL_FONT);
        StandardModeButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                //Use speed instead of random
                if (Math.random() < 0.5) {
                    setDrivingMode(false);
                } else {
                    Util.info("Standard Mode is only available while parked!");
                }
            }
        });

        JPanel ModeSwapPanel = new JPanel(new BorderLayout(20,20));
        ModeSwapPanel.add(DrivingModeButton,BorderLayout.WEST);
        ModeSwapPanel.add(StandardModeButton,BorderLayout.EAST);

        initDrivingMode();
        initStandardMode();

        //build
        window.add(Util.wrap(ModeSwapPanel),BorderLayout.NORTH);
        MainPanel = new JPanel();
        MainPanel.add(DrivingMode);
        MainPanel.add(StandardMode);
        window.add(MainPanel,BorderLayout.CENTER);
        setDrivingMode(false);
        window.setVisible(true);
        VehicleDataReceiver.initDataReceiver();
    }

    public static void initDrivingMode() {
        DrivingMode = new JPanel();
        DrivingMode.add(new JLabel("You are in Driving mode"));
    }

    public static void initStandardMode() {
        StandardMode = new JPanel();
        StandardMode.add(new JLabel("You are in Standard Mode"));
    }

}