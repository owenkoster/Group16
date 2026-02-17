import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class Main {

    static JFrame window;

    static JPanel DrivingMode;
    static JPanel StandardMode;

    public static void setDrivingMode(boolean drivingMode) {
            DrivingMode.setVisible(drivingMode);
            StandardMode.setVisible(!drivingMode);
    }

    public static void main(String[] args) {
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
        window.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        window.setSize(800,500);
        window.setLocationRelativeTo(null);

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

        //init Driving Mode
        DrivingMode = new JPanel();
        DrivingMode.add(new JLabel("You are in Driving mode"));
        //init Standard Mode
        StandardMode = new JPanel();
        StandardMode.add(new JLabel("You are in Standard Mode"));
        //build
        window.add(Util.wrap(ModeSwapPanel),BorderLayout.NORTH);
        window.add(DrivingMode,BorderLayout.WEST);
        window.add(StandardMode,BorderLayout.EAST);
        setDrivingMode(false);
        window.setVisible(true);
    }
}

