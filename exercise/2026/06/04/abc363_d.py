N = int(input())

d = 0
pow10 = 10
n = 0

while True:
    nn = n + pow10
    d += 1
    if d > 1:
        nn -= pow10 // 10
    if N <= nn:
        break

    n = nn
    if d % 2 == 0:
        pow10 *= 10

N -= n
if d == 1:
    print(N - 1)
elif d == 2:
    print(N * 11)
else:
    a = pow(10, (d - 1) // 2) + N - 1
    upper = str(a)
    if d % 2 == 0:
        lower = upper[::-1]
    else:
        lower = upper[:-1][::-1]

    print(upper + lower)
