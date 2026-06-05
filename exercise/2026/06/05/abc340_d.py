from heapq import heappush, heappop

N = int(input())

g = [[] for _ in range(N)]

for i in range(N - 1):
    a, b, x = map(int, input().split())
    g[i].append((i + 1, a))
    g[i].append((x - 1, b))

q = []
heappush(q, (0, 0))

dist = [float("inf")] * N
dist[0] = 0

while q:
    t, u = heappop(q)
    if u == N - 1:
        break

    for v, w in g[u]:
        if dist[v] <= t + w:
            continue
        dist[v] = t + w
        heappush(q, (t + w, v))

print(dist[N - 1])
