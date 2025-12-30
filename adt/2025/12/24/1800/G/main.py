from collections import deque


N, M = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

edges = set((min(a, b), max(a, b)) for a, b in zip(A, B))
graph = [[] for _ in range(N + 1)]

for a, b in edges:
    graph[a].append(b)
    graph[b].append(a)

visited = [-1] * (N + 1)
for i in range(1, N + 1):
    if visited[i] != -1:
        continue

    queue = deque()
    queue.append((i, 0))
    while queue:
        u, n = queue.popleft()
        if visited[u] == n:
            continue
        if visited[u] == 1 - n:
            print("No")
            exit()

        visited[u] = n
        for v in graph[u]:
            if visited[v] == n:
                print("No")
                exit()
            if visited[v] == 1 - n:
                continue
            queue.append((v, 1 - n))

print("Yes")
