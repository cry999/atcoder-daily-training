import heapq

N, M = map(int, input().split())
g = [[] for _ in range(N+1)]

for _ in range(M):
    a, b, c, d = map(int, input().split())
    g[a].append((b, c, d))
    g[b].append((a, c, d))

dist = [float('inf')] * (N+1)
tree = [0] * (N+1)

dist[1] = 0
queue = [(0, 0, 1)]  # (dist, -tree, node)

count = 0
while queue:
    d, t, v = heapq.heappop(queue)
    t = -t

    for nv, nd, nt in g[v]:
        if dist[nv] < d+nd:
            continue
        if dist[nv] == d+nd and tree[nv] >= t+nt:
            continue
        count += 1
        dist[nv] = d+nd
        tree[nv] = t+nt
        heapq.heappush(queue, (dist[nv], -tree[nv], nv))

# print(count)
print(dist[N], tree[N])
