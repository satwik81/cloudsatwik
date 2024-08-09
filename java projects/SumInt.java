import java.util.*;
import java.io.*;
class SumInt
{ 
public static void main(String args[ ]) throws IOException
{
BufferedReader br = new BufferedReader ( new InputStreamReader(System.in) );
System.out.println ("Enter a line of integers : ");
String str= br.readLine ();
StringTokenizer sc=new StringTokenizer (str," ");
System.out.println ("The integers are:");
int total=0;
while(sc.hasMoreTokens())
{ 
int k=Integer.parseInt(sc.nextToken());
System.out.println (k);
total = total+k;
}
System.out.println("Sum of all integers:"+total);
}
 }