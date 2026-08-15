# >>> atcoder-stat >>>
# started_at  = 2026-08-08T07:39:11+09:00
# solved_at   = 2026-08-08T07:57:04+09:00
# duration_ms = 1073144
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
MOD = 998244353

N, M, K = map(int, input().split())

# dp[i][j] := A[i] を j にする場合の数
dp = [1] * (M + 1)
dp[0] = 0  # A[i] は 1 以上なので 0 はありえない

# prefix_sum[j] := i-1 番目が j 以下の場合の数
prefix_sum = [0] * (M + 1)
# suffix_sum[j] := i-1 番目が j 以上の場合の数
suffix_sum = [0] * (M + 1)

for _ in range(N - 1):
    prefix_sum[0] = dp[0]
    for j in range(M):
        prefix_sum[j + 1] = prefix_sum[j] + dp[j + 1]

    suffix_sum[M] = dp[M]
    for j in range(M, 0, -1):
        suffix_sum[j - 1] = suffix_sum[j] + dp[j - 1]

    for j in range(1, M + 1):
        dp[j] = 0
        if j - K >= 0:
            dp[j] += prefix_sum[j - K]
        if j + K <= M:
            dp[j] += suffix_sum[j + K]
        if K == 0:
            dp[j] -= prefix_sum[j] - prefix_sum[j - 1]
        dp[j] %= MOD
    # print(f"[DEBUG] {dp=}")

print(sum(dp) % MOD)
