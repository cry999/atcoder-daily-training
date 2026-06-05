from collections import deque

N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    a, b = map(int, input().split())
    g[a].append(b)

q = deque()
q.append((1, 0))

dist = [float("inf")] * (N + 1)

ans = -1
while q:
    u, d = q.popleft()

    if u == 1 and d > 0:
        ans = d
        break

    for v in g[u]:
        if dist[v] <= d + 1:
            continue
        dist[v] = d + 1
        q.append((v, d + 1))

print(ans)
