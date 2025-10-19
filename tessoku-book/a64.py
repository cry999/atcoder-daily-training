import heapq


N, M = map(int, input().split())

nodes = [[] for _ in range(N+1)]
for _ in range(M):
    A, B, C = map(int, input().split())
    nodes[A].append((B, C))
    nodes[B].append((A, C))

dist = [float('inf')] * (N+1)
dist[1] = 0
queue = [(0, 1)]

while queue:
    d, v = heapq.heappop(queue)

    for nv, nc in nodes[v]:
        nd = d + nc
        if dist[nv] <= nd:
            continue
        dist[nv] = nd
        heapq.heappush(queue, (nd, nv))

for d in dist[1:]:
    if d == float('inf'):
        print(-1)
    else:
        print(d)
