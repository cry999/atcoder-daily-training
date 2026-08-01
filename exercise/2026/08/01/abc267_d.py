# >>> atcoder-stat >>>
# started_at  = 2026-08-01T19:59:39+09:00
# solved_at   = 2026-08-01T20:08:05+09:00
# duration_ms = 506687
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
# dp[i] := A[j] までの要素を使って、長さ i の数列を作った時の最大スコア
dp = [-INF] * (M + 1)
dp[0] = 0

for a in A:
    for i in range(M, 0, -1):
        # a を i 番目に使って良いか？
        dp[i] = max(dp[i], dp[i - 1] + i * a)
print(dp[M])
