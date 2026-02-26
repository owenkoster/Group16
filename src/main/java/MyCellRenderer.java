import javax.swing.*;
import javax.swing.border.CompoundBorder;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;

class MyCellRenderer extends JLabel implements ListCellRenderer<JLabel> {
    public MyCellRenderer() {
        setOpaque(true);
    }
    public Component getListCellRendererComponent(JList<? extends JLabel> list,
                                                  JLabel value,
                                                  int index,
                                                  boolean isSelected,
                                                  boolean cellHasFocus) {
        setText(value.getText());

        setFont(value.getFont());
        setIcon(value.getIcon());
        setBorder(new CompoundBorder(new LineBorder(Color.lightGray,2),new EmptyBorder(5,10,5,0)));
        value.setName(value.getText());
        Color background;
        Color foreground;
        JList.DropLocation dropLocation = list.getDropLocation();
        if (dropLocation != null
                && !dropLocation.isInsert()
                && dropLocation.getIndex() == index) {
            background = Color.BLUE;
            foreground = Color.WHITE;
        } else if (isSelected) {
            background = Color.lightGray;
            foreground = Color.black;
        } else {
            background = Color.WHITE;
            foreground = Color.BLACK;
        }
        setBackground(background);
        setForeground(foreground);
        return this;
    }
}