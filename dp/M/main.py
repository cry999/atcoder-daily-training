MOD = 10**9 + 7

N, K = map(int, input().split())
(*a,) = map(int, input().split())

dp = [[0] * (K + 1) for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    for k in range(K + 1):
        if k == 0:
            dp[i + 1][k] = dp[i][k]
        elif k - a[i] <= 0:
            dp[i + 1][k] = dp[i + 1][k - 1] + dp[i][k]
        else:
            dp[i + 1][k] = dp[i + 1][k - 1] + (dp[i][k] - dp[i][k - a[i] - 1]) % MOD
        dp[i + 1][k] %= MOD

print(dp[-1][K])
