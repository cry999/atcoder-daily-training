# >>> atcoder-stat >>>
# started_at  = 2026-08-01T20:30:13+09:00
# solved_at   = 2026-08-01T20:43:57+09:00
# duration_ms = 824951
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
MOD = 10**9 + 7
S = int(input())

dp = [0] * (max(S, 3) + 1)
dp[3] = 1
for i in range(4, S + 1):
    dp[i] = (dp[i - 1] + dp[i - 3]) % MOD
print(dp[S])
