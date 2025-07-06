import java.io.*;
interface StackADT
{
int SIZE = 10;
void push(int elem);
void pop();
void traverse();
}
class MyClass implements StackADT
{
int top = -1;
int stk[];
MyClass()
{
stk = new int[SIZE];
}
public void push(int elem)
{
if ( top == (SIZE-1) )
System.out.println("Stack is full");
else
{ top++;
stk[top] = elem;
}
 }
public void pop()
{
if ( top == -1)
System.out.println("Stack is empty, no element to delete");
else
{ 
System.out.println("The deleted element is : " + stk[top]);
top--;
}
 }
public void traverse()
{ 
if ( top == -1)
System.out.println("Stack is empty, no elementsto traverse");
else
{
 System.out.println("Elements in the stack are : ");
for(int i= top; i>= 0 ; i--)
System.out.println(stk[i]);
}
 }
 }
class StackDemo
{
 public static void main(String args[]) throws IOException
{
BufferedReader br = new BufferedReader( new InputStreamReader(System.in));
MyClass ob = new MyClass();
int ch, elem;
do
{
System.out.println("1.Push");
System.out.println("2.Pop");
System.out.println("3.Traverse");
System.out.println("4.Exit");
System.out.println("Enter your choice : ");
ch = Integer.parseInt(br.readLine());
switch( ch ) { case 1 : System.out.println("Enter element to insert :");
elem = Integer.parseInt( br.readLine() );
ob.push(elem);
break;
case 2: ob.pop();
break;
case 3: ob.traverse();
break;
case 4: System.exit(0);
}
}
while( ch>0 && ch< 5);
}
}