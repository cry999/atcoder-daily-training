from math import isqrt


N, M = map(int, input().split())

ans = 0
for i in range(1, isqrt(M) + 1):
    if M % i != 0:
        continue
    if M // i >= N:
        ans = max(ans, i)
    if i >= N:
        ans = max(ans, M // i)
print(ans)
