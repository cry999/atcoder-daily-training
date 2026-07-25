# >>> atcoder-stat >>>
# started_at  = 2026-07-23T07:56:42+09:00
# solved_at   = 2026-07-23T08:23:13+09:00
# duration_ms = 1591722
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())  # head
(*B,) = map(int, input().split())  # body
(*C,) = map(int, input().split())  # tail

INF = 10**18
dp = [-INF] * 3
dp[0] = A[0]
for i in range(1, N):
    ndp = [] * 3
    dp = [
        dp[0] + A[i],
        max(dp[0], dp[1]) + B[i],
        max(dp[1], dp[2]) + C[i],
    ]

print(dp[2])
