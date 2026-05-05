N, P = map(int, input().split())
MOD = 998244353

p = P * pow(100, MOD - 2, MOD) % MOD
q = (1 - p) % MOD

dp = [0] * (N + 1)
dp[0] = 0
dp[1] = 1

for i in range(2, N + 1):
    dp[i] = p * (1 + dp[i - 2]) + q * (1 + dp[i - 1])
    dp[i] %= MOD

print(dp[N])
