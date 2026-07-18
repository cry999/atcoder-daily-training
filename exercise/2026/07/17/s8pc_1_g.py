N, M = map(int, input().split())
g = [[] for _ in range(N)]

for _ in range(M):
    s, t, d, time = map(int, input().split())
    s, t = s - 1, t - 1
    g[s].append((t, d, time))
    g[t].append((s, d, time))

INF = 10**18
dp_time = [[INF] * (1 << N) for _ in range(N)]
dp_time[0][1 << 0] = 0

dp_routes = [[0] * (1 << N) for _ in range(N)]
dp_routes[0][1 << 0] = 1

for s in range(1 << N):
    for u in range(N):
        if s & (1 << u) == 0:
            continue

        for v, d, time in g[u]:
            if s & (1 << v):
                continue
            if dp_time[u][s] + d > time:
                continue
            ns = s | (1 << v)
            # dp_time[v][ns] = min(dp_time[v][ns], dp_time[u][s] + d)
            if dp_time[v][ns] > dp_time[u][s] + d:
                dp_time[v][ns] = dp_time[u][s] + d
                dp_routes[v][ns] = dp_routes[u][s]
            elif dp_time[v][ns] == dp_time[u][s] + d:
                dp_routes[v][ns] += dp_routes[u][s]

ALL = (1 << N) - 1
min_time = -1
min_time_routes = 0
for u in range(N):
    for v, d, time in g[u]:
        if v != 0:
            continue
        if dp_time[u][ALL] + d > time:
            continue
        if 0 <= min_time < dp_time[u][ALL] + d:
            continue
        if min_time == dp_time[u][ALL] + d:
            min_time_routes += dp_routes[u][ALL]
        else:
            min_time = dp_time[u][ALL] + d
            min_time_routes = dp_routes[u][ALL]

if min_time == -1:
    print("IMPOSSIBLE")
else:
    print(min_time, min_time_routes)
