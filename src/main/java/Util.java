import javax.swing.*;
import java.awt.*;

public class Util {

    public static Font SMALL_FONT = new Font("Arial",Font.PLAIN,24);

    public static JPanel wrap(Component comp) {
        JPanel wrap = new JPanel();
        wrap.add(comp);
        return wrap;
    }

    public static void info(String message) {
        JOptionPane.showMessageDialog(Main.window,message,"Info",JOptionPane.WARNING_MESSAGE);
    }

    public static String properCase(String s) {
        s = s.toLowerCase();
        s = s.replace("_"," ");
        if (s.charAt(0) >= 97 && s.charAt(0) <= 122) {
            s = (char)(s.charAt(0) - 32) +  s.substring(1);
        }
        for (int i = 1; i < s.length(); i++) {
            if (s.charAt(i-1) == ' ' && s.charAt(i) > 97 && s.charAt(i) <= 122) {
                s = s.substring(0,i) + (char)(s.charAt(i)-32) + s.substring(i+1);
            }
        }
        s = s.replace("Maf","MAF");
        s = s.replace("Dtc","DTC");
        s = s.replace("B1s","B1S");
        s = s.replace("Rpm","RPM");
        s = s.replace("Elm","ELM");
        return s;
    }

}
