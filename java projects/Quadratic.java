class Quadratic
{
 public static void main(String args[])
{
double a=5,b=10,c=2,r1,r2,d;
d=(b*b)-(4*a*c);
if(d==0)
{ 
System.out.println("Roots are real and equal");
System.out.println("The roots are : " + (-b/(2*a) ) );
}
else if(d<0)
System.out.println("The roots are imaginary");
else if(d>0)
{
 r1=-b+(Math.sqrt(d))/(2*a);
r2=-b-(Math.sqrt(d))/(2*a);
System.out.println("root1=" + r1);
System.out.println("root2=" + r2);
}
 }
 }