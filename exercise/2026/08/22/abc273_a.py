# >>> atcoder-stat >>>
# started_at  = 2026-08-22T20:49:08+09:00
# solved_at   = 2026-08-22T20:50:43+09:00
# duration_ms = 95032
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

dp = [0] * (N + 1)
dp[0] = 1
for k in range(N):
    dp[k + 1] = (k + 1) * dp[k]

print(dp[N])
