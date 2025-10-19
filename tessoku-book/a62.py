import heapq


N, M = map(int, input().split())
visited = [False] * (N+1)
visited[0] = True

nodes = [[] for _ in range(N+1)]
for _ in range(M):
    A, B = map(int, input().split())
    nodes[A].append(B)
    nodes[B].append(A)

queue = [1]
visited[1] = True
while queue:
    node = heapq.heappop(queue)

    for next in nodes[node]:
        if visited[next]:
            continue
        visited[next] = True
        heapq.heappush(queue, next)

print(f'The graph is {"" if all(visited) else "not "}connected.')
