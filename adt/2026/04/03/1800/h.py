N, M, K = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(M)]
(*E,) = map(int, input().split())

costs = [float("inf")] * (N + 1)
costs[1] = 0

for e in E:
    u, v, c = edges[e - 1]
    costs[v] = min(costs[v], costs[u] + c)


if costs[N] == float("inf"):
    print(-1)
else:
    print(costs[N])
