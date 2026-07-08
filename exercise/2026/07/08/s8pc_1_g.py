N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    s, t, d, time = map(int, input().split())
    s, t = s - 1, t - 1
    g[s].append((t, d, time))
    g[t].append((s, d, time))

INF = 10**18
dist = [[INF] * (1 << N) for _ in range(N)]
dist[0][1] = 0
cnt = [[0] * (1 << N) for _ in range(N)]
cnt[0][1] = 1

for s in range(1 << N):
    for u in range(N):
        if dist[u][s] == INF:
            continue
        for v, d, time in g[u]:
            if s & (1 << v):
                continue
            ndist = dist[u][s] + d
            if ndist > time:
                continue
            ns = s | (1 << v)
            if ndist == dist[v][ns]:
                cnt[v][ns] += cnt[u][s]
            elif ndist < dist[v][ns]:
                dist[v][ns] = dist[u][s] + d
                cnt[v][ns] = cnt[u][s]

min_dist = INF
min_cnt = 0
ALL = (1 << N) - 1
for u in range(N):
    for v, d, time in g[u]:
        if v == 0 and dist[u][ALL] + d <= time:
            if min_dist > dist[u][ALL] + d:
                min_dist = dist[u][ALL] + d
                min_cnt = cnt[u][ALL]
            elif min_dist == dist[u][ALL] + d:
                min_cnt += cnt[u][ALL]

if min_dist == INF:
    print("IMPOSSIBLE")
    exit()
print(min_dist, min_cnt)
