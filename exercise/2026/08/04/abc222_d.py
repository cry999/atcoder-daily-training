# >>> atcoder-stat >>>
# started_at  = 2026-08-04T07:59:02+09:00
# solved_at   = 2026-08-04T08:06:53+09:00
# duration_ms = 471850
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353

N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

M = 3000

dp = [0] * (M + 1)
dp[0] = 1

for i in range(N):
    # 累積和をとる
    for x in range(M):
        dp[x + 1] = (dp[x + 1] + dp[x]) % MOD

    dp = [dp[x] if A[i] <= x <= B[i] else 0 for x in range(M + 1)]

print(sum(dp) % MOD)
