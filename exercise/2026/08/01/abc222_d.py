# >>> atcoder-stat >>>
# started_at  = 2026-08-01T20:09:04+09:00
# solved_at   = 2026-08-01T20:25:05+09:00
# duration_ms = 961477
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

M = 3000
MOD = 998244353

# dp[i][j] := C[i] が j である場合の数。
# 計算を楽にするために、C[i-1] は j 以下の値にしておく。(C'[i-1] とする。)
# dp[i][j] = sum(dp[i-1][0], ..., dp[i-1][j]) + dp[i][j-1]
#          = dp'[i-1][j] + dp[i][j-1]

dp = [[0] * (M + 1) for _ in range(N + 1)]
dp[0] = [1] * (M + 1)

for i in range(N):
    for j in range(M + 1):
        if A[i] <= j <= B[i]:
            dp[i + 1][j] += dp[i][j]
        if j - 1:
            dp[i + 1][j] += dp[i + 1][j - 1]
        dp[i + 1][j] %= MOD

    print("[DEBUG]", dp[i + 1])

print(dp[N][M] % MOD)
