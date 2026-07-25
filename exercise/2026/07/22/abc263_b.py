# >>> atcoder-stat >>>
# started_at  = 2026-07-22T15:43:16+09:00
# solved_at   = 2026-07-22T15:47:37+09:00
# duration_ms = 261206
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*P,) = map(int, input().split())

# dp[i] := 人 i は人 1 の何代目の子孫か?
dp = [0] * N

for i in range(1, N):
    dp[i] = dp[P[i - 1] - 1] + 1
print(dp[N - 1])
