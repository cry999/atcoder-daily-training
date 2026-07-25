# >>> atcoder-stat >>>
# started_at  = 2026-07-23T13:04:39+09:00
# solved_at   = 2026-07-23T13:11:36+09:00
# duration_ms = 417210
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
    (*X,) = map(int, input().split())  # N
    (*Y,) = map(int, input().split())  # N-1

    # dp[weather] := 最後の天気が weather である時の最大嬉しさ
    dp = [0] * 2
    dp[int(S[0] == "S")] -= X[0]

    for i in range(N - 1):
        dp = [
            max(dp[0], dp[1] + Y[i]) - (X[i + 1] if S[i + 1] == "R" else 0),
            max(dp[0], dp[1]) - (X[i + 1] if S[i + 1] == "S" else 0),
        ]

    print(max(dp))
