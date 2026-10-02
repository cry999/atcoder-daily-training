# >>> atcoder-stat >>>
# started_at  = 2026-10-02T09:24:33+09:00
# solved_at   = 2026-10-02T09:37:59+09:00
# duration_ms = 806222
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = input()
K = int(input())

dp = [[[0] * 2 for _ in range(K + 1)] for _ in range(len(N) + 1)]
dp[0][0][0] = 1

for i in range(len(N)):
    for less in range(2):
        n = int(N[i])

        # 0 を追加する場合: k は増えない & n が 0 以外なら less 確定
        for k in range(K + 1):
            dp[i + 1][k][less or n != 0] += dp[i][k][less]

        # 1~9 を追加する場合: k は増える
        limit = 9 if less else n
        for d in range(1, limit + 1):
            for k in range(K):
                nless = less or d < n
                dp[i + 1][k + 1][nless] += dp[i][k][less]

ans = sum(dp[len(N)][K])
print(ans)
