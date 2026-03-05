N = int(input())

n = [0] * 10

while N:
    n[N % 10] += 1
    N //= 10

if all(n[i] == i for i in [1, 2, 3]):
    print("Yes")
else:
    print("No")
