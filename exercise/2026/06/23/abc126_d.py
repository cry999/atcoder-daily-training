import sys

input = sys.stdin.readline

N = int(input())
g = [[] for _ in range(N)]
color = [0] * N

for i in range(N - 1):
    u, v, w = map(int, input().split())
    g[u - 1].append((v - 1, w))
    g[v - 1].append((u - 1, w))

q = [(0, -1)]
for u, p in q:
    for v, w in g[u]:
        if v == p:
            continue
        if w % 2:
            color[v] = 1 - color[u]
        else:
            color[v] = color[u]
        q.append((v, u))

for c in color:
    print(c)
