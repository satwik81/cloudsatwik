import java.util.*;
class guess
{
public static void main(String args[])
{
 int s;
System.out.println("Welcome to the guess game ");
System.out.println("please enter your name");
Scanner sc= new Scanner(System.in);
String name= sc.next();
System.out.println("Hello " + name);
System.out.println("please enter any number to start the game ");
Scanner scs= new Scanner(System.in);
s=scs.nextInt();
if(s>0)
{
Random r = new Random();
int num= r.nextInt(20);
for( int i=0;i<5;i++)
{
System.out.println("Guess the number");
Scanner sc1= new Scanner(System.in);
int x=sc1.nextInt();
switch(x){
case 1:if(x==num)
{
System.out.println("congratulations  "+ name);
break;
}
case 2:if(x>num)
{
System.out.println("Please guess lower than ur number ");
break;
}
case 3:if(x<num)
{
System.out.println("please guess higher than ur number");
break;
}
if(i==4)
{
System.out.println("Game Over.....");
break;
}
}
}
}
}
}




