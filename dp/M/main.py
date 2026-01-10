N, K = map(int, input().split())
(*a,) = map(int, input().split())

MOD = 10**9 + 7

dp = [[0] * (K + 1) for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    ai = a[i]

    dp[i + 1][0] = dp[i][0]
    for k in range(K):
        dp[i + 1][k + 1] = dp[i + 1][k] + dp[i][k + 1]
        if k >= ai:
            dp[i + 1][k + 1] -= dp[i][k - ai]
        dp[i + 1][k + 1] %= MOD

print(dp[-1][-1])
