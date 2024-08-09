class Demo
{
int fib(int n)
{
 if(n==1)
return (1);
else if(n==2)
return (1);
else
return (fib(n-1)+fib(n-2));
}
}
class Fib1
{ 
public static void main(String args[])
{
Demo ob=new Demo();
System.out.println("The 10th fibonacci element is " + ob.fib(10));
}
 }