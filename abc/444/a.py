N = int(input())

a = N % 10
N //= 10
b = N % 10
N //= 10
c = N % 10

if a == b == c:
    print("Yes")
else:
    print("No")
