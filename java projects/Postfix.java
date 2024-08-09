import java.io.*;
import java.util.*;
class MyClass
{
int isoperator(char symbol)
{
if(symbol == '+' || symbol == '-' || symbol == '*' || symbol == '/' )
return 1;
else
return 0;
}
double evaluate(String postfix)
{
Stack<Double> stk = new Stack<Double>();
int i;
char symbol;
double oper1,oper2,result;
for(i=0;i<postfix.length();i++)
{
symbol = postfix.charAt(i);
if (isoperator(symbol)==0)
stk.push((double)(symbol-48) );
else
{
oper2 = stk.pop();
oper1 = stk.pop();
result = calculate(oper1,symbol,oper2);
stk.push(result);
}
}//end of for.
result = stk.pop();
return(result);
}
double calculate(double oper1,char symbol,double oper2)
{ 
switch(symbol)
{
case '+' : return(oper1+oper2);
case '-' : return(oper1-oper2);
case '*' : return(oper1* oper2);
case '/' : return(oper1/oper2);
default : return(0);
} 
} 
}
class Postfix
{
public static void main(String args[]) throws IOException
{ 
BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
System.out.println("Enter postfix expression : ");
String postfix = br.readLine();
MyClass ob = new MyClass();
System.out.println("The result value is : " + ob.evaluate(postfix));
}
 }