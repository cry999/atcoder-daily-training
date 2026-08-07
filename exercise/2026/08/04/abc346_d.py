# >>> atcoder-stat >>>
# started_at  = 2026-08-04T07:33:46+09:00
# solved_at   = 2026-08-04T07:47:05+09:00
# duration_ms = 799551
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*S,) = map(int, input())
(*C,) = map(int, input().split())

INF = 10**18
dp = [[INF] * 2 for _ in range(2)]
dp[0][S[0]] = 0
dp[0][1 - S[0]] = C[0]

for i in range(1, N):
    ndp = [[INF] * 2 for _ in range(2)]

    ndp[0][S[i]] = dp[0][1 - S[i]]
    ndp[0][1 - S[i]] = dp[0][S[i]] + C[i]

    ndp[1][S[i]] = min(dp[1][1 - S[i]], dp[0][S[i]])
    ndp[1][1 - S[i]] = min(dp[1][S[i]], dp[0][1 - S[i]]) + C[i]

    dp = ndp

print(min(dp[1]))
