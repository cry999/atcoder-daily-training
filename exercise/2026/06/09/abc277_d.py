import sys
from collections import defaultdict

sys.setrecursionlimit(10**7)

N, M = map(int, input().split())
(*A,) = map(int, input().split())

hist = defaultdict(int)
hist_mod = defaultdict(list)
for a in A:
    hist[a] += 1

for i, a in enumerate(hist.keys()):
    hist_mod[a % M].append(i)

L = len(hist)
B = list(hist.items())
g = [[] for _ in range(L)]
for i, (a, cnt) in enumerate(B):
    for j in hist_mod[(a + 1) % M]:
        g[i].append(j)

dist = [-1] * L


def dfs(i: int) -> int:
    if dist[i] >= 0:
        return dist[i]

    a, cnt = B[i]
    dist[i] = 0
    for j in g[i]:
        dist[i] = max(dist[i], dfs(j))
    dist[i] += a * cnt
    return dist[i]


ans = 0
for i in range(L):
    if dist[i] >= 0:
        continue

    ans = max(dfs(i), ans)

print(sum(A) - ans)
