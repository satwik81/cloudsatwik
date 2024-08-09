class Producer implements Runnable
{ 
StringBuffer sb;
Producer ()
{ 
sb = new StringBuffer();
}
public void run ()
{
synchronized (sb)
{
for (int i=1;i<=5;i++)
{
 try
{
sb.append (i + " : ");
Thread.sleep (500);
System.out.println (i + " appended");
}
catch (InterruptedException ie){}
}
sb.notify ();
} 
} 
}
class Consumer implements Runnable
{
 Producer prod;
Consumer (Producer prod)
{ 
this.prod = prod;
}
public void run()
{
synchronized (prod.sb)
{
try
{
prod.sb.wait ();
}
catch (Exception e) { }
System.out.println (prod.sb);
} 
} 
}
class Communicate
{
public static void main(String args[])
{
Producer obj1 = new Producer ();
Consumer obj2 = new Consumer (obj1);
Thread t1 = new Thread (obj1);
Thread t2 = new Thread (obj2);
t2.start ();
t1.start ();
}
}