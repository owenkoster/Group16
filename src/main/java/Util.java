import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class Util {

    public static Font SMALL_FONT = new Font("Arial",Font.PLAIN,24);
    public static Font BIG_FONT = new Font("Arial",Font.PLAIN,32);

    public static JPanel wrap(Component comp) {
        JPanel wrap = new JPanel();
        wrap.add(comp);
        return wrap;
    }

    public static void info(String message) {
        JFrame popup = new JFrame();
        popup.setTitle("Info");
        popup.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        popup.setSize(message.length()*15,200);
        popup.setLocationRelativeTo(null);
        JLabel label = new JLabel(message);
        label.setFont(SMALL_FONT);
        JButton ok = new JButton("ok");
        ok.setFont(SMALL_FONT);
        ok.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                popup.dispose();
            }
        });
        JPanel panel = new JPanel(new BorderLayout(10,15));
        panel.add(wrap(label),BorderLayout.NORTH);
        panel.add(wrap(ok),BorderLayout.CENTER);
        popup.add(panel);
        popup.setVisible(true);
    }

}
