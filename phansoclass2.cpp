#include <iostream>
using namespace std;

int ucln(int a,int b){
    if(b==0) return a;
    return ucln(b,a%b);
}

int bcnn(int a,int b){
    return a / ucln(a,b) * b;
}

class phanso{
private:
    int tu,mau;
public:
    phanso(){
        tu=mau=0;
    }
    phanso(int,int);
    friend istream& operator >> (istream&,phanso&);
    friend ostream& operator << (ostream&,phanso);
    void rutgon();
    friend phanso operator + (phanso,phanso);
};
phanso::phanso(int tu, int mau){
    this->tu=tu;
    this->mau=mau;
}

istream& operator >> (istream &in,phanso &a){
    in>>a.tu>>a.mau;
    return in;
}

ostream& operator << (ostream &out,phanso a){
    out<<a.tu<<"/"<<a.mau;
    return out;
}

void phanso::rutgon() {
    int g = ucln(tu,mau);
    tu /= g;
    mau /= g;
}

phanso operator + (phanso a,phanso b){
    phanso tong(1,1);
    int mauchung = bcnn(a.tu,a.mau);
    tong.tu = mauchung / a.mau * a.tu + mauchung / b.mau * b.tu;
    tong.mau = mauchung;
    int g = ucln(tong.tu,tong.mau);
    tong.tu/=g,tong.mau/=g;
    return tong;
}

int main(){
    phanso a(1,1), b(1,1);
    cin>>a>>b;
    a.rutgon();
    cout<<a+b;
}