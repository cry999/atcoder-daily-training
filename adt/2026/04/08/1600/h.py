MOD = 998244353
N, P = map(int, input().split())

dp = [0] * (N + 1)
dp[1] = 1

p = (P * pow(100, MOD - 2, MOD)) % MOD
q = (1 - p) % MOD

for i in range(2, N + 1):
    dp[i] = ((dp[i - 1] + 1) * q + (dp[i - 2] + 1) * p) % MOD

print(dp[N])
