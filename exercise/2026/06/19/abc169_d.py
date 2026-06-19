from math import isqrt

N = int(input())

ans = 0
for d in range(2, isqrt(N) + 1):
    if N == 1:
        break

    n = 0
    while N % d == 0:
        N //= d
        n += 1

    ans += max(0, (-1 + isqrt(8 * n + 1)) // 2)

if N != 1:
    ans += 1

print(ans)
