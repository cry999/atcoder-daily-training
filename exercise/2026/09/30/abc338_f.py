# >>> atcoder-stat >>>
# started_at  = 2026-09-30T10:59:42+09:00
# solved_at   = 2026-09-30T11:22:00+09:00
# duration_ms = 1338878
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
g = [[] for _ in range(N)]
for _ in range(M):
    u, v, w = map(int, input().split())
    g[u - 1].append((v - 1, w))

INF = float("inf")
dist = [[INF] * N for _ in range(N)]
for u in range(N):
    dist[u][u] = 0
    for v, w in g[u]:
        dist[u][v] = min(dist[u][v], w)

for k in range(N):
    for u in range(N):
        for v in range(N):
            dist[u][v] = min(dist[u][v], dist[u][k] + dist[k][v])

dp = [[INF] * N for _ in range(1 << N)]
for i in range(N):
    dp[1 << i][i] = 0

for s in range(1 << N):
    for u in range(N):
        if s & (1 << u) == 0:
            continue

        for v in range(N):
            ns = s | (1 << v)
            dp[ns][v] = min(dp[ns][v], dp[s][u] + dist[u][v])

ans = INF
for u in range(N):
    ans = min(ans, dp[-1][u])
if ans == INF:
    print("No")
else:
    print(ans)
