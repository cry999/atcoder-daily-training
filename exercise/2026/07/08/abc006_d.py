# >>> atcoder-stat >>>
# started_at  = 2026-07-08T17:20:02+09:00
# solved_at   = 2026-07-08T17:25:08+09:00
# duration_ms = 306131
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left

N = int(input())
deck = [int(input()) for _ in range(N)]

INF = N + 1

dp = [0] * N
L = [INF] * (N + 1)
L[0] = -1

for i in range(N):
    x = bisect_left(L, deck[i])
    L[x] = min(L[x], deck[i])
    dp[i] = x

print(N - max(dp))
