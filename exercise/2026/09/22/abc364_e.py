# >>> atcoder-stat >>>
# started_at  = 2026-09-22T16:35:52+09:00
# solved_at   = 2026-09-22T16:43:19+09:00
# duration_ms = 447932
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


N, X, Y = map(int, input().split())

# 考察
# 1. 甘さとしょっぱさの2軸で DP をすると 10^10 のオーダーになるので無理
# 2. N が小さいので、N と甘さの組み合わせで考える。
# 3. i 番目までの料理を処理して、甘さが x の時に n 個の料理を食べた場合のしょっぱさの最小値
INF = 10**18
dp = [[INF] * (N + 1) for _ in range(X + 1)]
dp[0][0] = 0

for _ in range(N):
    a, b = map(int, input().split())
    for x in range(X - a, -1, -1):
        for n in range(N):
            dp[x + a][n + 1] = min(dp[x + a][n + 1], dp[x][n] + b)

for n in range(N, -1, -1):
    for x in range(X + 1):
        if dp[x][n] <= Y:
            print(min(n + 1, N))
            exit()
