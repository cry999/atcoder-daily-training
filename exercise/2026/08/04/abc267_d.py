# >>> atcoder-stat >>>
# started_at  = 2026-08-04T07:54:59+09:00
# solved_at   = 2026-08-04T07:58:51+09:00
# duration_ms = 232841
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*A,) = map(int, input().split())

INF = float("inf")
# dp[i] := 長さ i の部分列を作った時の最大スコア
dp = [-INF] * (M + 1)
dp[0] = 0

for i in range(N):
    for j in range(M, 0, -1):
        dp[j] = max(dp[j], dp[j - 1] + j * A[i])

print(dp[M])
