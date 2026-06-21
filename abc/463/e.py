import sys
import heapq

input = sys.stdin.readline

INF = 10**18

N, M, Y = map(int, input().split())
g = [[] for _ in range(N + 3)]
ws = N + 1
wt = N + 2

g[ws].append((wt, Y))

for _ in range(M):
    u, v, t = map(int, input().split())
    g[u].append((v, t))
    g[v].append((u, t))

(*X,) = map(int, input().split())
for i, x in enumerate(X, 1):
    g[i].append((ws, x))
    g[wt].append((i, x))

q = [(0, 1)]
dist = [INF] * (N + 3)

while q:
    c, u = heapq.heappop(q)
    if dist[u] <= c:
        continue
    dist[u] = c

    for v, t in g[u]:
        if dist[v] <= c + t:
            continue
        heapq.heappush(q, (c + t, v))

print(*dist[2 : N + 1])
