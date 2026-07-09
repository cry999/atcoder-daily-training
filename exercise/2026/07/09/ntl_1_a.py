from math import isqrt

N = int(input())

n = N
ans = []
for d in range(2, isqrt(N) + 1):
    if d > n:
        break
    while n % d == 0:
        ans.append(d)
        n //= d
if n > 1:
    ans.append(n)
print(f"{N}: {' '.join(map(str, ans))}")
