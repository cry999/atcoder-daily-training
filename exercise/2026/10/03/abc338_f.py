# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:20:36+09:00
# solved_at   = 2026-10-03T11:27:05+09:00
# duration_ms = 389798
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

INF = float("inf")

N, M = map(int, input().split())
dist = [[INF] * N for _ in range(N)]
for i in range(N):
    dist[i][i] = 0
for _ in range(M):
    u, v, w = map(int, input().split())
    dist[u - 1][v - 1] = min(dist[u - 1][v - 1], w)

for k in range(N):
    for u in range(N):
        for v in range(N):
            dist[u][v] = min(dist[u][v], dist[u][k] + dist[k][v])

dp = [[INF] * N for _ in range(1 << N)]
for u in range(N):
    dp[1 << u][u] = 0

for s in range(1 << N):
    for u in range(N):
        if s & (1 << u) == 0:
            continue

        for v in range(N):
            if u == v or s & (1 << v):
                continue

            ns = s | (1 << v)
            dp[ns][v] = min(dp[ns][v], dp[s][u] + dist[u][v])

ans = min(dp[-1])
if ans == INF:
    print("No")
else:
    print(ans)
