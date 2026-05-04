# from heapq import heappop, heappush
from collections import deque

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for i in range(M):
    a, b, c = map(int, input().split())
    a, b = a - 1, b - 1

    g[a].append((b, c, i))
    g[b].append((a, c, i))

dist = [float("inf")] * N
dist[0] = 0
from_edge_idx = [-1] * N

# q = [(0, 0)]
q = deque([(0, 0)])

while q:
    # u, c = heappop(q)
    u, c = q.popleft()
    if dist[u] < c:
        continue

    for v, nc, i in g[u]:
        nc += c
        if dist[v] <= nc:
            continue
        dist[v] = nc
        # heappush(q, (v, nc))
        q.append((v, nc))
        from_edge_idx[v] = i

print(*[i + 1 for i in from_edge_idx if i != -1])
