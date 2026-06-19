N = int(input())
S = [input() for _ in range(N)]

dp = [[0] * 2 for _ in range(N + 1)]
dp[0][0] = dp[0][1] = 1

T = 0
F = 1
for i in range(N):
    if S[i] == "AND":
        # x_i が True かつ x_{i-1} までが True の場合
        dp[i + 1][T] = dp[i][T]
        # x_i が True かつ x_{i-1} までが False の場合
        # x_i が False の場合 (x_{i-1} まではどうでも良い)
        dp[i + 1][F] = dp[i][T] + 2 * dp[i][F]
    else:
        # x_i が False かつ x_{i-1} までが True の場合
        # x_i が True の場合 (x_{i-1} まではどうでも良い)
        dp[i + 1][T] = 2 * dp[i][T] + dp[i][F]
        # x_i が False かつ x_{i-1} までが False の場合
        dp[i + 1][F] = dp[i][F]

print(dp[N][T])
