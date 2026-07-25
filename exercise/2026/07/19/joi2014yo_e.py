from heapq import heappush, heappop

N, K = map(int, input().split())
taxi = [tuple(map(int, input().split())) for _ in range(N)]

g = [[] for _ in range(N)]

for _ in range(K):
    a, b = map(int, input().split())
    a, b = a - 1, b - 1

    g[a].append(b)
    g[b].append(a)

g2 = [[] for _ in range(N)]
for i in range(N):
    _, r = taxi[i]
    q = [(i, r)]
    visited = [False] * N
    visited[i] = True

    for u, r in q:
        if r == 0:
            continue
        for v in g[u]:
            if visited[v]:
                continue
            visited[v] = True
            g2[i].append(v)
            if r > 1:
                q.append((v, r - 1))

dist = [-1] * N
dist[0] = 0
q = [(0, 0)]
while q:
    d, u = heappop(q)
    if d != dist[u]:
        continue
    if u == N - 1:
        break

    c = taxi[u][0]
    for v in g2[u]:
        if 0 <= dist[v] <= dist[u] + c:
            continue
        dist[v] = dist[u] + c
        heappush(q, (dist[v], v))

print(dist[N - 1])
