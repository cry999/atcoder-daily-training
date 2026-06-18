from collections import deque

MOD = 10**9 + 7

N, M = map(int, input().split())
g = [[] for _ in range(N + 1)]

for _ in range(M):
    u, v = map(int, input().split())
    g[u].append(v)
    g[v].append(u)

dist = [-1] * (N + 1)
cnt = [0] * (N + 1)

q = deque()
q.append(1)
cnt[1] = 1

while q:
    u = q.popleft()

    for v in g[u]:
        if 0 <= dist[v] < dist[u] + 1:
            continue
        if dist[v] == dist[u] + 1:
            cnt[v] += cnt[u]
            cnt[v] %= MOD
            continue
        dist[v] = dist[u] + 1
        cnt[v] = cnt[u]
        q.append(v)

print(cnt[N])
