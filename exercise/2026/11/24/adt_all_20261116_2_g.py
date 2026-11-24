# >>> atcoder-stat >>>
# started_at  = 2026-11-24T10:17:29+09:00
# solved_at   = 2026-11-24T10:41:10+09:00
# duration_ms = 1421352
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
T = int(input())
for _ in range(T):
    N = int(input())
    S = input()

    dp = [[0] * 3 for _ in range(N + 1)]
    for i in range(N):
        dp[i + 1][0] += dp[i][0] + (S[i] == "1")
        dp[i + 1][1] += min(dp[i][0], dp[i][1]) + (S[i] == "0")
        dp[i + 1][2] += min(dp[i][1], dp[i][2]) + (S[i] == "1")

    print(min(dp[N]))
