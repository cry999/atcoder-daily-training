# >>> atcoder-stat >>>
# started_at  = 2026-07-04T11:34:52+09:00
# solved_at   = 2026-07-04T11:43:08+09:00
# duration_ms = 496356
# target_ms   = 900000
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
    (*X,) = map(int, input().split())
    Y = [0] * N
    Y[1:] = map(int, input().split())

    # dp[i][w] := i 日目の天気が w である時の嬉しさの最大値
    dp = [[0] * 2 for _ in range(N + 1)]
    SUNNY = 0
    RAINY = 1

    for i in range(N):
        dp[i + 1][SUNNY] = max(dp[i][SUNNY], dp[i][RAINY] + Y[i])
        dp[i + 1][RAINY] = max(dp[i])
        if S[i] == "S":
            dp[i + 1][RAINY] -= X[i]
        else:
            dp[i + 1][SUNNY] -= X[i]

    print(max(dp[N]))
