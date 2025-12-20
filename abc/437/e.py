import sys
from collections import defaultdict


sys.setrecursionlimit(10**7)

N = int(input())

A = []
for i in range(N):
    x, y = map(int, input().split())
    A.append((x, y, i+1))


g = [defaultdict(int) for _ in range(N+1)]
mapping = [i for i in range(N+1)]
same = [[i] for i in range(N+1)]
for x, y, idx in A:
    x = mapping[x]
    if g[x][y]:
        mapping[idx] = g[x][y]
        same[g[x][y]].append(idx)
    else:
        g[x][y] = idx

a = []


def dfs(x: int) -> list[int]:
    if x:
        a.extend(same[x])

    for _, idx in sorted(g[x].items()):
        dfs(idx)


dfs(0)
print(*a)
