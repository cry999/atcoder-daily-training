from collections import deque
from math import isqrt


N, M = map(int, input().split())

divisors: set[int] = set()
for d in range(1, isqrt(N) + 1):
    if N % d != 0:
        continue
    divisors.add(d % M)
    divisors.add((N // d) % M)

ans = [-1] * M
q: deque[int] = deque()

for d in divisors:
    ans[d] = 1
    q.append(d)

while q:
    r = q.popleft()
    for d in divisors:
        x = r * d % M
        if ans[x] != -1:
            continue
        ans[x] = ans[r] + 1
        q.append(x)

print(*ans, sep="\n")
