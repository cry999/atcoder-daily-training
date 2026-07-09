# >>> atcoder-stat >>>
# started_at  = 2026-07-09T14:18:21+09:00
# solved_at   = 2026-07-09T14:23:25+09:00
# duration_ms = 304322
# target_ms   = 900000
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


N, M = map(int, input().split())

INF = float("inf")
dist = [[INF] * N for _ in range(N)]

for _ in range(M):
    a, b, t = map(int, input().split())
    a, b = a - 1, b - 1
    dist[a][b] = dist[b][a] = t

for i in range(N):
    dist[i][i] = 0

for k in range(N):
    for a in range(N):
        for b in range(N):
            dist[a][b] = min(dist[a][b], dist[a][k] + dist[k][b])

ans = INF
for a in range(N):
    ans = min(ans, max(dist[a]))
print(ans)
