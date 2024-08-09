import java.util.*;
import java.io.*;
class CountWords
{
 public static void main(String args[]) throws IOException
{
 BufferedReader br = new BufferedReader(new InputStreamReader(
System.in) );
HashSet<String> hs = new HashSet<String>();
System.out.println("Enter a line of text : " );
String s1 = br.readLine();
StringTokenizer st1 = new StringTokenizer( s1 , " ");
while( st1.hasMoreTokens() ) { hs.add(st1.nextToken() );
}
Iterator it = hs.iterator();
while (it.hasNext() ) { int count = 0;
String a = (String) it.next();
StringTokenizer st2 = new StringTokenizer( s1, " ");
while( st2.hasMoreTokens() )
 {
 String b = (String) st2.nextToken();
if (a.equals ( b ) )
count++;
}
System.out.println(a + " count is : " + count);
} 
} 
}