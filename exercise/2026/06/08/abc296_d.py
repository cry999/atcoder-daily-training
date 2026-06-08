from math import isqrt

N, M = map(int, input().split())

if N**2 < M:
    print(-1)
    exit()

x = isqrt(M)

ans = -1
for a in range(1, x + 2):
    b = M // a
    if M % a != 0:
        b += 1
    if a <= N and b <= N and (ans > a * b or ans == -1):
        ans = a * b

print(ans)
