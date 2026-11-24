# >>> atcoder-stat >>>
# started_at  = 2026-11-24T13:27:42+09:00
# solved_at   = 2026-11-24T13:48:24+09:00
# duration_ms = 1242149
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
MOD = 998244353

N, M, K = map(int, input().split())
# dp[i][s] := i 番目までを決めて、合計が s 以下になる数列の個数
dp = [[0] * (K + 1) for _ in range(N + 1)]
for s in range(K + 1):
    dp[0][s] = 1

for i in range(N):
    # まずは i 番目までで s になる数を計算する
    for s in range(1, K + 1):
        dp[i + 1][s] = dp[i][s - 1]
        if s - M - 1 >= 0:
            dp[i + 1][s] -= dp[i][s - M - 1]
        dp[i + 1][s] %= MOD

    # 累積和にする
    print(f"[DEBUG] prev {dp=}")
    for s in range(K):
        dp[i + 1][s + 1] += dp[i + 1][s]
        dp[i + 1][s + 1] %= MOD
    print(f"[DEBUG] next {dp=}")

print(dp[N][K])
