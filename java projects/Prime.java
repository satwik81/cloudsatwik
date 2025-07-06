import java.io.*;
class Prime
{
 public static void main(String args[])throws IOException
{ 
int i,j,a=0,n;
BufferedReader br= new BufferedReader(new InputStreamReader (System.in) );
System.out.println("Enter range : " );
n = Integer.parseInt(br.readLine() );
for(i=2;i<=n;i++)
{ 
a=0;
for(j=2;j<i;j++)
{
if(i%j==0)
a=1;
}
if(a==0)
System.out.print(i + "\t");
}
}
}