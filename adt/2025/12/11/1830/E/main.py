N, M = map(int, input().split())

g = [[] for _ in range(N+1)]

for _ in range(M):
    a, b, c = map(int, input().split())
    g[a].append((b, c))
    g[b].append((a, c))

for i in range(1, N+1):
    g[0].append((i, 0))


queue = [(0, 0, 0)]  # (node, cost, visited)
ALL_VISITED = (1 << N) - 1

max_cost = 0
while queue:
    v, cost, visited = queue.pop()
    max_cost = max(max_cost, cost)
    if visited == ALL_VISITED:
        continue

    for nv, nc in g[v]:
        if visited & (1 << (nv-1)):
            continue

        queue.append((nv, cost+nc, visited | (1 << (nv-1))))

print(max_cost)
