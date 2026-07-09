# >>> atcoder-stat >>>
# started_at  = 2026-07-09T14:23:59+09:00
# solved_at   = 2026-07-09T14:28:47+09:00
# duration_ms = 288091
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
H, W = map(int, input().split())
dist = [list(map(int, input().split())) for _ in range(10)]

for k in range(10):
    for i in range(10):
        for j in range(10):
            dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

A = [list(map(int, input().split())) for _ in range(H)]
cost = 0
for pos in range(H * W):
    i, j = divmod(pos, W)
    if A[i][j] == -1:
        continue
    cost += dist[A[i][j]][1]
print(cost)
