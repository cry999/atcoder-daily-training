# >>> atcoder-stat >>>
# started_at  = 2026-07-23T16:50:22+09:00
# solved_at   = 2026-07-23T17:18:01+09:00
# duration_ms = 1659498
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
(*T,) = map(int, input())

# total_dp[bit] = i 文字目までで作られる部分文字列で bit に収束する部分文字列の個数
total_dp = [0] * 2
# i_dp[bit] = i 文字目を右端とする部分文字列で bit に収束する部分文字列の個数
i_dp = [0] * 2

for i in range(N):
    i_dp[:] = i_dp[1 - T[i]] + (1 - T[i]), i_dp[T[i]] + T[i]
    total_dp[:] = total_dp[0] + i_dp[0], total_dp[1] + i_dp[1]
print(total_dp[1])
