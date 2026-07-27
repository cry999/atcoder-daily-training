# >>> atcoder-stat >>>
# started_at  = 2026-07-25T18:40:31+09:00
# solved_at   = 2026-07-25T18:44:07+09:00
# duration_ms = 216340
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
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())
(*C,) = map(int, input().split())

# どのタイミングで A->B, B->C に遷移するかを考える。
INF = 10**18
dp = [-INF] * 3
dp[0] = A[0]

for i in range(1, N):
    dp = [
        dp[0] + A[i],
        max(dp[0], dp[1]) + B[i],
        max(dp[1], dp[2]) + C[i],
    ]

print(dp[2])
