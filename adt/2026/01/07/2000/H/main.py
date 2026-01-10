import heapq

N, M, K = map(int, input().split())
graph = [[] for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())
    graph[a].append(b)
    graph[b].append(a)

queue = []

for _ in range(K):
    p, h = map(int, input().split())
    heapq.heappush(queue, (-h, p))

visited = [False] * (N + 1)

while queue:
    neg_h, p = heapq.heappop(queue)
    h = -neg_h
    if visited[p]:
        continue
    visited[p] = True

    if h == 0:
        continue

    for v in graph[p]:
        if visited[v]:
            continue
        heapq.heappush(queue, (-(h - 1), v))

ans = list(filter(lambda u: visited[u], range(N + 1)))
print(len(ans))
print(*ans)
