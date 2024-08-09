#include <iostream>
#include <cmath>
#include <iomanip>

void calculateSimpleInterest(double principal,double rate,double time){
    double simpleInterest=(principal*rate*time)/100;
    std::cout<<"Simple Interest: "<<std::fixed<<std::setprecision(2)<<simpleInterest<<std::endl;
}

void calculateCompoundInterest(double principal,double rate,double time,int n){
    double amount=principal*pow((1+(rate/(n*100))),n*time);
    double compoundInterest=amount-principal;
    std::cout <<"Compound Interest: "<<std::fixed<<std::setprecision(2)<<compoundInterest<<std::endl;
}

int main() {
    double principal,rate,time;
    int n;
    char interestType;
    std::cout<<"Enter the principal amount: ";
    std::cin>>principal;
    std::cout<<"Enter the rate of interest (in %):";
    std::cin>>rate;
    std::cout<<"Enter the time period (in years): ";
    std::cin>>time;
    std::cout<<"Choose interest type (S for Simple Interest,C for Compound Interest): ";
    std::cin>>interestType;

    if(interestType=='S'||interestType=='s'){
        calculateSimpleInterest(principal,rate,time);
    } else if(interestType=='C'||interestType=='c'){
        std::cout<<"Enter the number of times interest is compounded per year: ";
        std::cin>>n;
        calculateCompoundInterest(principal,rate,time,n);
    } else{
        std::cout<<"Invalid interest type selected."<<std::endl;
    }

    return 0;
}
