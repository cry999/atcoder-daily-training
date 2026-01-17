from collections import deque

N, M, L, S, T = map(int, input().split())
graph = [[] for _ in range(N + 1)]
for _ in range(M):
    u, v, c = map(int, input().split())
    graph[u].append((v, c))

queue = deque()
queue.append((1, 0, 0))

visited = [False] * (N + 1)

while queue:
    u, cost, step = queue.popleft()
    if step == L:
        if not visited[u]:
            visited[u] = S <= cost <= T
        continue

    for v, c in graph[u]:
        if cost + c > T:
            continue
        queue.append((v, cost + c, step + 1))

print(*filter(lambda x: visited[x], range(N + 1)))
