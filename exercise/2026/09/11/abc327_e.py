# >>> atcoder-stat >>>
# started_at  = 2026-09-11T14:05:58+09:00
# solved_at   = 2026-09-11T14:10:03+09:00
# duration_ms = 245129
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from math import sqrt

N = int(input())
(*P,) = map(int, input().split())

INF = float("inf")
# dp[k] := k 個のコンテストを選択した時の最大パフォーマンス (変動部分のみ)
dp = [-INF] * (N + 1)
dp[0] = 0

for i, p in enumerate(P):
    for k in range(i, -1, -1):
        dp[k + 1] = max(dp[k + 1], dp[k] * 0.9 + p)

ans = -INF
d = 1
for k in range(N):
    ans = max(ans, dp[k + 1] / d - 1200 / sqrt(k + 1))
    d = d * 0.9 + 1
print(ans)
