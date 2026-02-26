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
        JOptionPane.showMessageDialog(Main.window,message,"Info",JOptionPane.WARNING_MESSAGE);
    }

}
