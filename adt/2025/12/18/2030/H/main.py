import heapq


N, M = map(int, input().split())
g = [[] for _ in range(N+1)]
for i in range(M):
    a, b, c = map(int, input().split())
    g[a].append((b, c, i))
    g[b].append((a, c, i))

dist = [(float('inf'), -1)]*(N+1)

queue = [(0, 1, -1)]
while queue:
    d, v, i = heapq.heappop(queue)
    if dist[v][0] <= d:
        continue
    dist[v] = (d, i)
    for nv, nd, ni in g[v]:
        if dist[nv][0] <= d+nd:
            continue
        heapq.heappush(queue, (d+nd, nv, ni))

print(*filter(lambda x: x, map(lambda x: x[1]+1, dist)))
