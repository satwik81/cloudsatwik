import java.awt.*;
import java.awt.event.*;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
class RegistrationPage 
{
public static void main(String args[]){
Frame f=new Frame("Registration Form");
CheckboxGroup cbg=new CheckboxGroup();
Label l1=new Label("First Name:");
Label l2=new Label("Last Name:");
Label l3=new Label("Gender");
Label l4=new Label("Address:");
Label l5=new Label("Mobile No:");
Label l6=new Label("");
Checkbox c1=new Checkbox("Male",cbg,false);
Checkbox c2=new Checkbox("Female",cbg,false);
TextField t1=new TextField();
TextField t2=new TextField();
TextField t3=new TextField();
TextField t4=new TextField();
Button b1=new Button("Submit");
l1.setBounds(20,45,70,20);
t1.setBounds(100,45,150,20);
l2.setBounds(20,95,70,20);
t2.setBounds(100,95,150,20);
l3.setBounds(20,135,100,20);
l4.setBounds(20,175,70,20);
l5.setBounds(20,210,70,20);
l6.setBounds(50,290,250,50);
t3.setBounds(100,175,150,20);
t4.setBounds(100,210,150,20);
c1.setBounds(120,135,100,20);
c2.setBounds(120,155,100,20);
b1.setBounds(150,250,50,50);
b1.addActionListener(new ActionListener(){
public void actionPerformed(ActionEvent e)
{
l6.setText("You have submitted your details successfully");
}});
f.addWindowListener(new WindowAdapter (){
public void windowClosing(WindowEvent we)
{
System.exit(0);
}
});
f.add(l1);
f.add(l2);
f.add(l3);
f.add(l5);
f.add(t1);
f.add(t2);
f.add(l4);
f.add(t4);
f.add(t3);
f.add(c1);
f.add(c2);
f.add(b1);
f.add(l6);
f.setSize(800,800);
f.setLayout(null);
f.setVisible(true);

}
}