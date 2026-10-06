# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:50:49+09:00
# solved_at   = 2026-10-03T11:54:43+09:00
# duration_ms = 234992
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = input()
K = int(input())

dp = [[0] * 2 for _ in range(K + 1)]
dp[0][0] = 1
for _, s in enumerate(N):
    n = int(s)
    ndp = [[0] * 2 for _ in range(K + 1)]

    for less in range(2):
        limit = 9 if less else n
        for d in range(limit + 1):
            nless = less or d < n
            if d:
                for k in range(K):
                    ndp[k + 1][nless] += dp[k][less]
            else:
                for k in range(K + 1):
                    ndp[k][nless] += dp[k][less]

    dp = ndp

print(sum(dp[K]))
