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
        if (s.contains("Maf")) s = s.substring(0,s.indexOf("Maf")) + "MAF" + s.substring(s.indexOf("Maf")+3);
        if (s.contains("Dtc")) s = s.substring(0,s.indexOf("Dtc")) + "DTC" + s.substring(s.indexOf("Dtc")+3);
        if (s.contains("B1s")) s = s.substring(0,s.indexOf("B1s")) + "B1S" + s.substring(s.indexOf("B1s")+3);
        if (s.contains("Rpm")) s = s.substring(0,s.indexOf("Rpm")) + "RPM" + s.substring(s.indexOf("Rpm")+3);
        if (s.contains("Elm")) s = s.substring(0,s.indexOf("Elm")) + "ELM" + s.substring(s.indexOf("Elm")+3);
        return s;
    }

}
