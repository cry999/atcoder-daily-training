N, M = map(int, input().split())


g = [[] for _ in range(N+1)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a].append(b)
    g[b].append(a)

visited = [False] * (N+1)
cnt = 0
for i in range(1, N+1):
    if visited[i]:
        continue
    visited[i] = True

    queue = [i]
    edges = 0
    nodes = 0
    check_edges = set()
    while queue:
        u = queue.pop()
        nodes += 1
        for v in g[u]:
            edge_name = f'{min(u, v)}-{max(u, v)}'
            if edge_name not in check_edges:
                edges += 1
                check_edges.add(edge_name)
            if visited[v]:
                continue
            visited[v] = True
            queue.append(v)
    cnt += nodes*(nodes-1)//2 - edges

print(cnt)
