# >>> atcoder-stat >>>
# started_at  = 2026-07-25T19:54:02+09:00
# solved_at   = 2026-07-25T20:03:10+09:00
# duration_ms = 548878
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353
N, M, K = map(int, input().split())

dp = [0] * (K + 1)
dp[0] = 1

for _ in range(N):
    for k in range(K):
        dp[k + 1] += dp[k]

    ndp = [0] * (K + 1)
    for k in range(1, K + 1):
        ndp[k] = dp[k - 1]
        if k - M - 1 >= 0:
            ndp[k] -= dp[k - M - 1]
    dp = [x % MOD for x in ndp]

print(sum(dp) % MOD)
