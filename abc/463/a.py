from math import gcd

X, Y = map(int, input().split())
d = gcd(X, Y)

if X // d == 16 and Y // d == 9:
    print("Yes")
else:
    print("No")
