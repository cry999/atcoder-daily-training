# >>> atcoder-stat >>>
# started_at  = 2026-07-23T16:39:02+09:00
# solved_at   = 2026-07-23T16:50:04+09:00
# duration_ms = 662900
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
(*X,) = map(int, input().split())
bonus = [0] * (N + 1)
for _ in range(M):
    cnt, bonus_price = map(int, input().split())
    bonus[cnt] += bonus_price

# dp[c] := カウンタが c のときのスコアの最大値
# INF = float("inf")
dp = [0] * (N + 1)
dp[0] = 0

for i in range(N):
    zero = dp[0]
    for c in range(i + 1, 1, -1):
        dp[c] = dp[c - 1] + X[i] + bonus[c]  # 表
        dp[0] = max(dp[0], dp[c - 1]) + bonus[0]  # 裏
    dp[1] = zero + X[i] + bonus[1]  # 表
    dp[0] = max(dp[0], zero) + bonus[0]

print(max(dp))
