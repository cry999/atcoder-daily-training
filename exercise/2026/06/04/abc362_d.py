from heapq import heappush, heappop

N, M = map(int, input().split())
(*A,) = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    u, v, w = map(int, input().split())
    g[u - 1].append((v - 1, w))
    g[v - 1].append((u - 1, w))

dist = [float("inf")] * N

q = []
heappush(q, (A[0], 0))
dist[0] = A[0]

while q:
    d, u = heappop(q)
    if dist[u] < d:
        continue

    for v, w in g[u]:
        if dist[v] <= d + w + A[v]:
            continue
        dist[v] = d + w + A[v]
        q.append((dist[v], v))

print(*dist[1:])
