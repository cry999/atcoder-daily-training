from heapq import heappush as push, heappop as pop

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for i in range(M):
    a, b, c = map(int, input().split())
    a, b = a - 1, b - 1

    g[a].append((b, c, i))
    g[b].append((a, c, i))

dist = [float("inf")] * N
used = [False] * M

q = [(0, 0, -1)]

while q:
    d, u, i = pop(q)
    if dist[u] < d:
        continue

    dist[u] = d
    if i >= 0:
        used[i] = True

    for v, c, i in g[u]:
        if dist[v] <= d + c:
            continue

        dist[v] = d + c
        push(q, (d + c, v, i))

ans = [i + 1 for i in range(M) if used[i]]
print(*ans)
