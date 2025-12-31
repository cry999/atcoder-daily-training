from math import isqrt


N = int(input())
k0 = isqrt(N)

ans = 0
for i in range(1, k0 + 1):
    ans += i * (N // i - N // (i + 1))

for i in range(1, N // (k0 + 1) + 1):
    ans += N // i

print(ans)
