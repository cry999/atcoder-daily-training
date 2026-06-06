from collections import deque

N1, N2, M = map(int, input().split())
g = [[] for _ in range(N1 + N2 + 1)]
for _ in range(M):
    a, b = map(int, input().split())
    g[a].append(b)
    g[b].append(a)

dist = [float("inf")] * (N1 + N2 + 1)
dist[1] = 0
dist[N1 + N2] = 0

q = deque()
q.append(1)
q.append(N1 + N2)

while q:
    u = q.popleft()

    for v in g[u]:
        if dist[v] <= dist[u] + 1:
            continue
        dist[v] = dist[u] + 1
        q.append(v)

m1 = 0
m2 = 0

for i in range(1, N1 + 1):
    m1 = max(m1, dist[i])
for i in range(N1 + 1, N1 + N2 + 1):
    m2 = max(m2, dist[i])

print(m1 + m2 + 1)  # 追加する辺の数をたし忘れない
