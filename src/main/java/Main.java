import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.*;
import javax.swing.plaf.FontUIResource;

import org.jfree.chart.*;
import org.jfree.chart.axis.*;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.DefaultXYItemRenderer;
import org.jfree.chart.ui.RectangleInsets;
import org.jfree.data.Range;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class Main {

    static JFrame window;

    static JPanel MainPanel;
    static JPanel DrivingMode;
    static JPanel StandardMode;
    static JPanel ModeSwapPanel;
    static JPanel ConnectingPanel;

    static XYSeriesCollection dataset;
    static XYSeriesCollection seriesCollection;
    static double[][] currentData = new double[2][10];

    // This would normally be like 1, but for testing higher values make more sense
    public static final double DRIVING_MODE_SPEED_THRESHOLD = 100;

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
        UIManager.put("OptionPane.font",new FontUIResource(Util.SMALL_FONT));
        UIManager.put("OptionPane.messageFont",new FontUIResource(Util.SMALL_FONT));
        //UIManager.put("OptionPane.buttonFont",new FontUIResource(Util.SMALL_FONT));
        UIManager.put("Button.font",new FontUIResource(Util.SMALL_FONT));
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
                    //pythonProcess.destroy();
                    VehicleDataReceiver.sendShutdownCommand();
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
                //  Switch 50 for 1 on real vehicle instead of emulator
                if (VehicleDataReceiver.speed < DRIVING_MODE_SPEED_THRESHOLD) {
                    setDrivingMode(false);
                } else {
                    Util.info("Standard Mode is only available while parked!");
                }
            }
        });

        ModeSwapPanel = new JPanel(new BorderLayout(20,20));
        ModeSwapPanel.add(DrivingModeButton,BorderLayout.WEST);
        ModeSwapPanel.add(StandardModeButton,BorderLayout.EAST);

        ConnectingPanel = new JPanel();
        JLabel connectLabel = new JLabel("Connecting to your vehicle...");
        connectLabel.setFont(Util.SMALL_FONT);
        ConnectingPanel.add(connectLabel);

        initDrivingMode();
        initStandardMode();

        //build
        window.add(Util.wrap(ModeSwapPanel),BorderLayout.NORTH);
        MainPanel = new JPanel();
        MainPanel.add(DrivingMode);
        MainPanel.add(StandardMode);
        MainPanel.add(Util.wrap(ConnectingPanel));
        window.add(MainPanel,BorderLayout.CENTER);
        MainPanel.setVisible(true);
        ModeSwapPanel.setVisible(false);
        ConnectingPanel.setVisible(true);
        DrivingMode.setVisible(false);
        StandardMode.setVisible(false);
        window.setVisible(true);
        VehicleDataReceiver.initDataReceiver();
    }

    public static void updateUI() {
        SwingUtilities.invokeLater( () -> {
            XYSeries oldSeries = dataset.getSeries(0);
            XYSeries newSeries = new XYSeries(oldSeries.getKey());
            for (int i = 0; i < oldSeries.getItemCount(); i++) {
                newSeries.add(oldSeries.getX(i).doubleValue() - 1.0, oldSeries.getY(i).doubleValue());
            }
            newSeries.add(0,VehicleDataReceiver.speed);
            dataset.removeSeries(0);
            dataset.addSeries(newSeries);
        });
        if (VehicleDataReceiver.speed > DRIVING_MODE_SPEED_THRESHOLD) {
            setDrivingMode(true);
        }
    }

    public static void initDrivingMode() {
        DrivingMode = new JPanel(new BorderLayout(10,10));
        XYPlot plot = new XYPlot();
        dataset = new XYSeriesCollection();
        dataset.addSeries(new XYSeries("SPEED"));
        plot.setDataset(dataset);
        plot.setAxisOffset(new RectangleInsets(10,10,10,10));
        plot.setDomainAxis(new NumberAxis("Time (seconds)"));
        plot.setRangeAxis(new NumberAxis("Speed (MPH)"));
        DefaultXYItemRenderer renderer = new DefaultXYItemRenderer();
        renderer.setLegendTextFont(10,Util.SMALL_FONT);
        plot.setRenderer(renderer);
        plot.getDomainAxis().setLabelFont(Util.SMALL_FONT);
        plot.getDomainAxis().setTickLabelFont(Util.SMALL_FONT);
        plot.getDomainAxis().setRange(new Range(-60,0));
        plot.getRangeAxis().setAutoRangeMinimumSize(40);
        plot.getRangeAxis().setLabelFont(Util.SMALL_FONT);
        plot.getRangeAxis().setTickLabelFont(Util.SMALL_FONT);
        plot.setFixedLegendItems(null);
        JFreeChart chart = new JFreeChart(plot);
        chart.setTitle("Speed (last 60 seconds)");
        chart.removeLegend();
        ChartPanel graph = new ChartPanel(chart);
        graph.setPreferredSize(new Dimension(400,300));
        DrivingMode.add(graph,BorderLayout.WEST);
    }

    public static void initStandardMode() {
        StandardMode = new JPanel();
        StandardMode.add(new JLabel("You are in Standard Mode"));
    }

}