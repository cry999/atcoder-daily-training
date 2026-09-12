# >>> atcoder-stat >>>
# started_at  = 2026-09-12T18:04:34+09:00
# solved_at   = 2026-09-12T18:13:55+09:00
# duration_ms = 561314
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


# n 個食べて、甘さが i の時のしょっぱさの最小値を DP する。

N, X, Y = map(int, input().split())
dp = [[math.inf] * (X + 1) for _ in range(N + 1)]
dp[0][0] = 0
for i in range(N):
    a, b = map(int, input().split())

    for j in range(i, -1, -1):
        for x in range(X - a + 1):
            dp[j + 1][x + a] = min(dp[j + 1][x + a], dp[j][x] + b)

for n in range(N, -1, -1):
    print(f"[DEBUG] {n=}, {dp[n]=}")
    for x in range(X + 1):
        if dp[n][x] <= Y:
            print(min(N, n + 1))
            exit()
