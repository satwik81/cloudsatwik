import java.io.*;
class FileProp
{ 
public static void main(String args[]) throws IOException
{
 BufferedReader br = new BufferedReader(new InputStreamReader (System.in));
System.out.println("Enter file name :");
String fname = br.readLine();
File f = new File (fname);
System.out.println ("File name: " + f.getName ());
System.out.println ("Path:"+ f.getPath ());
System.out.println ("Absolute Path:"+ f.getAbsolutePath ());
System.out.println ("Parent:"+ f.getParent ());
System.out.println ("Exists:"+ f.exists ());
if ( f.exists() ) 
{
System.out.println ("Is writable: "+ f.canWrite ());
System.out.println ("Is readable: "+ f.canRead ());
System.out.println ("Is executable: "+ f.canExecute ());
System.out.println ("Is directory: "+ f.isDirectory());
System.out.println ("File size in bytes: "+ f.length());
} 
} 
}