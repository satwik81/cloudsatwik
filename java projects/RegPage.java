import java.awt.*;
import java.awt.event.*;
class RegPage
{
public static void main(String args[])
{
Color ch = Color.red;
Frame f=new Frame("                              				                      REGISTRATION PAGE                                                                    ");
f.setBackground(ch);
CheckboxGroup cbg=new CheckboxGroup();
Label l=new Label("NAME");
Label l1=new Label("AGE");
Label l2=new Label("GENDER");
Label l3=new Label("EMAILID");
Label l4=new Label("ADDRESS");
Label l5=new Label();
Checkbox c=new Checkbox("Male",cbg,true);
Checkbox c1=new Checkbox("Female",cbg,false);
TextField t=new TextField();
TextField t1=new TextField();
TextField t2=new TextField();
TextArea t3=new TextArea();				
f.add(l);
l.setBounds(50,50,100,30);                           
f.add(l1);
l1.setBounds(50,70,100,30);
f.add(l2);
l2.setBounds(50,90,100,30); 
f.add(l3);
l3.setBounds(50,130,100,30);
f.add(l4);
l4.setBounds(50,150,100,30);
f.add(t);
t.setBounds(150,50,100,20);
f.add(t1);
t1.setBounds(150,70,100,20);
f.add(c);
c.setBounds(150,90,100,30);
f.add(c1);
c1.setBounds(250,90,100,30);
f.add(t2);
t2.setBounds(150,130,100,20);
f.add(t3);
t3.setBounds(150,150,150,150);
Button b=new Button("REGISTER");
f.add(b);
b.setBounds(300,500,100,30);
f.add(l5);
l5.setBounds(300,550,200,30);
b.addActionListener(new ActionListener(){
public void actionPerformed(ActionEvent e)
{
l5.setText("REGISTERED SUCCESSFULLY");
}});
t.addKeyListener(new KeyAdapter(){
public void keyPressed(KeyEvent e)
{     
         if(e.getKeyCode() == KeyEvent.VK_ENTER)
	{
         t1.requestFocus();
         };

}});
t1.addKeyListener(new KeyAdapter(){
public void keyPressed(KeyEvent e)
{
if(e.getKeyCode() == KeyEvent.VK_ENTER)
	{
         t2.requestFocus();
         };
}});
t2.addKeyListener(new KeyAdapter(){
public void keyPressed(KeyEvent e)
{
if(e.getKeyCode() == KeyEvent.VK_ENTER)
	{
         t3.requestFocus();
         };
}});      
f.setSize(800,800);
f.setLayout(null);
f.setVisible(true);
f.addWindowListener(new WindowAdapter(){
public void windowClosing(WindowEvent we)
{
System.exit(0);
};
});
}
}
