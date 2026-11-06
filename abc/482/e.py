from collections import defaultdict


N = int(input())

g: list[list[int]] = [[] for _ in range(N)]
for _ in range(N - 1):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u].append(v)
    g[v].append(u)

(*C,) = map(int, input().split())

ans = 0
count: defaultdict[int, int] = defaultdict(int)

for
