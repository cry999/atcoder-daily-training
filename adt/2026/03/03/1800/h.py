N, P = map(int, input().split())
MOD = 998244353

dp = [0] * (N + 1)

dp[0] = 0
dp[1] = 1

p = P * pow(100, MOD - 2, MOD) % MOD
q = (100 - P) * pow(100, MOD - 2, MOD) % MOD

for i in range(2, N + 1):
    dp[i] = q * (dp[i - 1] + 1) + p * (dp[i - 2] + 1)
    dp[i] %= MOD


print(dp[N])
