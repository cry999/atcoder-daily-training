# >>> atcoder-stat >>>
# started_at  = 2026-11-07T07:27:00+09:00
# <<< atcoder-stat <<<
from itertools import permutations

N, M = map(int, input().split())

g1: list[list[int]] = [[] for _ in range(N)]
for _ in range(M):
    a, b = map(int, input().split())
    a -= 1
    b -= 1
    g1[a].append(b)
    g1[b].append(a)

g2: list[list[int]] = [[] for _ in range(N)]
for _ in range(M):
    c, d = map(int, input().split())
    c -= 1
    d -= 1
    g2[c].append(d)
    g2[d].append(c)

for q in permutations(range(N)):
    pass
