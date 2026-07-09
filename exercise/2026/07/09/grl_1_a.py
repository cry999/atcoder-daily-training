import heapq

V, E, r = map(int, input().split())
g = [[] for _ in range(V)]
for _ in range(E):
    s, t, d = map(int, input().split())
    g[s].append((t, d))

dist = [-1] * V
dist[r] = 0
q = [(0, r)]

while q:
    d, u = heapq.heappop(q)
    for v, dd in g[u]:
        if 0 <= dist[v] <= d + dd:
            continue
        dist[v] = d + dd
        heapq.heappush(q, (dist[v], v))

for d in dist:
    print(d if d >= 0 else "INF")
