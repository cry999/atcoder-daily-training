import heapq


N, M, X = map(int, input().split())

g = [[] for _ in range(2*N+1)]

for u in range(1, N+1):
    g[u].append((u+N, X))
    g[u+N].append((u, X))

for _ in range(M):
    u, v = map(int, input().split())
    g[u].append((v, 1))
    g[v+N].append((u+N, 1))


queue = [(0, 1)]  # (cost, node)
costs = [float('inf')] * (2*N+1)
costs[1] = 0

while queue:
    cost, u = heapq.heappop(queue)

    for v, nc in g[u]:
        if costs[v] > cost+nc:
            costs[v] = cost+nc
            heapq.heappush(queue, (costs[v], v))

print(min(costs[N], costs[2*N]))
