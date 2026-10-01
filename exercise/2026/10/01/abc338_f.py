# >>> atcoder-stat >>>
# started_at  = 2026-10-01T08:37:39+09:00
# solved_at   = 2026-10-01T08:46:09+09:00
# duration_ms = 510243
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import math
import sys

input = sys.stdin.readline


N, M = map(int, input().split())
g = [[] for _ in range(N)]
for _ in range(M):
    u, v, w = map(int, input().split())
    g[u - 1].append((v - 1, w))

# 考察
# 1. 負の辺がある
# 2. 負の辺がなければ、単純な巡回セールスマン問題。bit DP で型がつく。
# 3. 負の辺があるが、負の閉路はないので、最適値は求められる。
# 4. 負の辺の影響をどう考慮するか？ -> 各移動最初に最短経路を求めておく。

min_dist = [[math.inf] * N for _ in range(N)]
for u in range(N):
    min_dist[u][u] = 0
    for v, w in g[u]:
        min_dist[u][v] = w

for k in range(N):
    for u in range(N):
        for v in range(N):
            min_dist[u][v] = min(min_dist[u][v], min_dist[u][k] + min_dist[k][v])

dp = [[math.inf] * N for _ in range(1 << N)]
for u in range(N):
    dp[1 << u][u] = 0

for s in range(1 << N):
    for src in range(N):
        if s & (1 << src) == 0:
            continue

        for dst in range(N):
            if s & (1 << dst) != 0:
                continue

            ns = s | (1 << dst)
            dp[ns][dst] = min(dp[ns][dst], dp[s][src] + min_dist[src][dst])

ans = min(dp[-1])
if ans == math.inf:
    print("No")
else:
    print(ans)
