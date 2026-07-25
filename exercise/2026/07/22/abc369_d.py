# >>> atcoder-stat >>>
# started_at  = 2026-07-22T19:03:52+09:00
# solved_at   = 2026-07-22T19:08:40+09:00
# duration_ms = 288119
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

# dp[i] := i (0/1) 匹のモンスターを倒した時の最大経験値。
# i は偶奇を表す。
dp = [0] * 2
dp[1] = -float("inf")  # 初期状態で奇数引き倒すことは不可能

for i in range(N):
    ndp = [0] * 2
    x = A[i]

    ndp[1] = max(dp[0] + x, dp[1])
    ndp[0] = max(dp[1] + 2 * x, dp[0])

    dp = ndp

print(max(dp))
