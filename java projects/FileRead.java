import java.io.*;
class FileRead
{ 
public static void main(String args[]) throws IOException
{
int ch,ctr=1;
String fname;
BufferedReader br = new BufferedReader(new InputStreamReader (System.in));
System.out.print("Enter a file name: ");
fname=br.readLine();
FileInputStream fin =new FileInputStream(fname);
System.out.print(ctr+" ");
while((ch=fin.read())!=-1)
{
System.out.print((char)ch);
if(ch=='\n')
{
ctr++;
System.out.print(ctr+" ");
} 
}
fin.close();
} 
}