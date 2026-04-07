from heapq import heappush as hpush, heappop as hpop
from atcoder.string import z_algorithm

N = int(input())
S = sorted(input().split(), reverse=True)

q = []
s = 0
ans = 0

for i in range(1, N):
    s1, s2 = S[i - 1 : i + 1]

    z = z_algorithm(s1 + s2)
    f = z[len(s1)]

    hpush(q, -f)
    s += f

    while -q[0] > f:
        t = -hpop(q)
        hpush(q, -f)
        s -= t
        s += f

    ans += s

print(ans)
