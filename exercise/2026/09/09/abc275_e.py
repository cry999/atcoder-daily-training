# >>> atcoder-stat >>>
# started_at  = 2026-09-09T21:19:55+09:00
# solved_at   = 2026-09-09T21:39:00+09:00
# duration_ms = 1145326
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
# dp[i][j] := i 回の操作が終わった時にマス j にいる確率
dp = [[0] * (N + 1) for _ in range(K + 1)]
dp[0][0] = 1

inv_m = pow(M, MOD - 2, MOD)

for i in range(K):
    print(f"[DEBUG] === {i=} === ")
    for j in range(N + 1):
        for k in range(1, M + 1):
            print(f"[DEBUG] {j=} {k=}")
            x = j - k
            if 0 <= x < N:
                print(f"[DEBUG]   {x=} -> {j=}")
                dp[i + 1][j] += dp[i][x] * inv_m % MOD
            x = 2 * N - j - k
            if N - k < x < N:
                print(f"[DEBUG]   {x=} -> {j=}")
                dp[i + 1][j] += dp[i][x] * inv_m % MOD
        dp[i + 1][j] %= MOD
print(f"[DEBUG] {dp=}")
print(sum(dp[i][N] for i in range(K + 1)) % MOD)
