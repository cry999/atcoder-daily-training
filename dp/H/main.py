H, W = map(int, input().split())
a = [input() for _ in range(H)]

MOD = 10**9 + 7
dp = [0] * W
dp[0] = 1
for i in range(H):
    for j in range(W):
        if a[i][j] == "#":
            dp[j] = 0
        elif j - 1 >= 0:
            dp[j] += dp[j - 1]
            dp[j] %= MOD
print(dp[-1])
