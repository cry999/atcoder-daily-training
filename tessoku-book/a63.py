import heapq


N, M = map(int, input().split())

nodes = [[] for _ in range(N+1)]

for _ in range(M):
    A, B = map(int, input().split())
    nodes[A].append(B)
    nodes[B].append(A)

visited = [-1] * (N+1)
queue = [(0, 1)]
visited[1] = 0

while queue:
    dist, pos = heapq.heappop(queue)

    for next in nodes[pos]:
        if visited[next] > -1:
            continue

        visited[next] = dist+1
        heapq.heappush(queue, (dist+1, next))

for i in range(1, N+1):
    print(visited[i])
