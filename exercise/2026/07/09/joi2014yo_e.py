import heapq

N, K = map(int, input().split())

# (運賃, 最大移動距離)
taxi = [(0, 0)]
for _ in range(N):
    taxi.append(tuple(map(int, input().split())))

g = [[] for _ in range(N + 1)]
for _ in range(K):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)

g2 = [[] for _ in range(N + 1)]
for u in range(1, N + 1):
    q = [(taxi[u][1], u)]
    visited = [False] * (N + 1)
    visited[u] = True
    for d, cur in q:
        if d == 0:
            continue
        for nxt in g[cur]:
            if visited[nxt]:
                continue
            visited[nxt] = True
            g2[u].append(nxt)
            if d - 1 >= 0:
                q.append((d - 1, nxt))

# (コスト, 現在地)
q = [(0, 1)]
costs = [-1] * (N + 1)
costs[1] = 0

while q:
    cost, cur = heapq.heappop(q)
    if cur == N:
        break

    cost += taxi[cur][0]
    for nxt in g2[cur]:
        if 0 <= costs[nxt] <= cost:
            continue
        costs[nxt] = cost
        heapq.heappush(q, (cost, nxt))
print(costs[N])
