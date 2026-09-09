# >>> atcoder-stat >>>
# started_at  = 2026-09-09T21:39:27+09:00
# solved_at   = 2026-09-09T22:00:52+09:00
# duration_ms = 1285043
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
from math import sqrt

N = int(input())
(*P,) = map(int, input().split())

INF = float("inf")

dp = [-INF] * (N + 1)
dp[0] = 0.0

for i, p in enumerate(P):
    for j in range(i + 1, 0, -1):
        dp[j] = max(dp[j], 0.9 * dp[j - 1] + p)

ans = -INF
denom = 0.0

for k in range(1, N + 1):
    denom = 0.9 * denom + 1
    ans = max(ans, dp[k] / denom - 1200 / sqrt(k))

print(ans)
