# >>> atcoder-stat >>>
# started_at  = 2026-08-04T08:07:11+09:00
# solved_at   = 2026-08-04T08:10:41+09:00
# duration_ms = 210426
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 10**9 + 7
S = int(input())

dp = [0] * (S + 1)
if S >= 3:
    dp[3] = 1
for s in range(3, S):
    dp[s + 1] = (dp[s] + dp[s - 2]) % MOD

print(dp[S])
