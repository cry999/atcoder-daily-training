MOD = 998244353
N, K = map(int, input().split())

ranges = [tuple(map(int, input().split())) for _ in range(K)]

dp = [0] * (N + 1)
dp[1] = 1
dp[2] = -1
for i in range(1, N + 1):
    dp[i] += dp[i - 1]
    for l, r in ranges:
        if i + l > N:
            continue

        dp[i + l] += dp[i]
        dp[i + l] %= MOD
        if i + r + 1 <= N:
            dp[i + r + 1] -= dp[i]
            dp[i + r + 1] %= MOD

print(dp[N] % MOD)
