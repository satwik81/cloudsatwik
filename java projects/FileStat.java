import java.io.*;
class FileStat
{ 
public static void main(String args[]) throws IOException
{ 
int pre=' ' , ch , ctr=0 , L=0 , w=1;
String fname;
BufferedReader br=new BufferedReader(new InputStreamReader (System.in));
System.out.print("Enter a file name: ");
fname=br.readLine();
FileInputStream fin = new FileInputStream(fname);
while((ch=fin.read())!=-1)
{ //char count
if(ch!=' ' && ch!='\n')
ctr++;
//line count
if(ch=='\n')
L++;
//word count
if(ch==' ' && pre!=' ')
w++;
pre=ch;
}
System.out.println("Char count="+ctr);
System.out.println("Word count="+(w+(L-1)));
System.out.println("Line count="+L);
} 
}