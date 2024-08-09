import java.io.*;
import java.util.*;
class Infix_Postfix
{
public static void main(String[] args) throws IOException
{
BufferedReader br = new BufferedReader( new InputStreamReader (System.in));
System.out.println("Enter Infix Expression : ");
String s= br.readLine();
Stack<Character> st=new Stack<Character>();
String output="";
int i=0,len=s.length();
char x;
st.push('@');
while(len!=0)
{ 
char c=s.charAt(i);
if(c=='(')
{
 st.push(c);
}
else if(c=='+'||c=='-'||c=='*'||c=='/'||c=='^'||c=='$')
{
 check(st,c,output);
st.push(c);
}
else if(c==')')
{
 while((x=(Character)st.pop())!='(')
{ output=output+x;
} }
else
{ 
output+=s.charAt(i);
}
i=i+1;
len--; }
while((x=(Character)st.pop())!='@')
{ 
output+=x;
}
System.out.println("postfix Expression is : "+ output);
}
static void check(Stack st,char c,String output)
{
while(priority(c)<=priority((Character)st.peek()))
output=output+st.pop();
}
static int priority(char ch)
{ 
if(ch=='+'||ch=='-')
return(1);
else if(ch=='*'||ch=='/')
return(2);
else if(ch=='$'||ch=='^')
return(3);
else
return(0);
}
 }
