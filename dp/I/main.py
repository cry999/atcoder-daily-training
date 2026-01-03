N = int(input())
(*p,) = map(float, input().split())
p = [0.0] + p

dp = [[0.0] * (N + 1) for _ in range(N + 1)]
dp[0][0] = 1.0

for i in range(1, N + 1):
    for j in range(i + 1):
        dp[i][j] = dp[i - 1][j] * (1 - p[i])
        if j > 0:
            dp[i][j] += dp[i - 1][j - 1] * p[i]

print(sum(dp[N][(N + 1) // 2 :]))
