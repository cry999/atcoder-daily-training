MOD = 10**9 + 7


K = input()
D = int(input())

k_digits = [int(c) for c in K]

n = len(k_digits)
# dp[i][d] = i+1 桁で各桁の数字の総和を D で割ったあまりが d の数の個数
dp = [[0] * D for _ in range(n)]
for k in range(10):
    dp[0][k % D] += 1
for i in range(n - 1):
    for d in range(D):
        for x in range(10):
            # i+1 桁の各桁の総和を D で割ったあまりが d の数字の最上位に
            # x を追加する。
            dp[i + 1][(d + x) % D] += dp[i][d]
            dp[i + 1][(d + x) % D] %= MOD


offset = 0
ans = 0
for i in range(n - 1):
    kd = k_digits[i]
    for x in range(kd):
        ans += dp[n - i - 2][(D - x - offset) % D]
        ans %= MOD
    offset = (offset + kd) % D

for x in range(k_digits[-1] + 1):
    ans += (offset + x) % D == 0
    ans %= MOD

print((ans - 1) % MOD)
