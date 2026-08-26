# >>> atcoder-stat >>>
# started_at  = 2026-08-22T20:45:37+09:00
# solved_at   = 2026-08-22T20:47:54+09:00
# duration_ms = 137097
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

dp = [0] * N

for i in range(1, N):
    dp[i] = dp[P[i - 1] - 1] + 1

print(dp[N - 1])
