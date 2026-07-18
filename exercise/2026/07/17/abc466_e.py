# >>> atcoder-stat >>>
# started_at  = 2026-07-17T20:00:34+09:00
# solved_at   = 2026-07-17T20:18:27+09:00
# duration_ms = 1073002
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

N, K = map(int, input().split())

INF = 10**18
dp = [-INF] * (2 * K + 1)
dp[0] = 0

for _ in range(N):
    ndp = [-INF] * (2 * K + 1)
    a, b = map(int, input().split())

    ndp[0] = dp[0] + a
    for k in range(1, 2 * K + 1):
        ndp[k] = max(dp[k], dp[k - 1]) + (a if k % 2 == 0 else b)

    dp = ndp

print(max(dp))
