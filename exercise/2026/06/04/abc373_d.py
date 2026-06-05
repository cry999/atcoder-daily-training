from collections import deque

N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    u, v, w = map(int, input().split())
    g[u - 1].append((v - 1, w))
    g[v - 1].append((u - 1, -w))

ans = [0] * N
visited = [False] * N

for u in range(N):
    if visited[u]:
        continue

    q = deque()
    q.append(u)
    visited[u] = True

    while q:
        u = q.popleft()

        for v, w in g[u]:
            if visited[v]:
                continue
            visited[v] = True
            ans[v] = ans[u] + w
            q.append(v)

print(*ans)
