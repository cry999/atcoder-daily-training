MOD = 998244353

S = input()
N = len(S)

# dp[i][j] := i 文字目までを処理した時に左側に孤立した ( が j こ残っている場合の数
dp = [[0] * (N + 1) for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    if S[i] == "(" or S[i] == "?":
        for j in range(N):
            dp[i + 1][j + 1] += dp[i][j]
            dp[i + 1][j + 1] %= MOD
    if S[i] == ")" or S[i] == "?":
        for j in range(N):
            dp[i + 1][j] += dp[i][j + 1]
            dp[i + 1][j] %= MOD

print(dp[N][0])
