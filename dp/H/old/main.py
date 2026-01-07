H, W = map(int, input().split())
a = [input() for _ in range(H)]
dp = [[0] * W for _ in range(H)]
dp[0][0] = 1

MOD = 10**9 + 7

for h in range(H):
    for w in range(W):
        if h + 1 < H and a[h + 1][w] == ".":
            dp[h + 1][w] += dp[h][w]
            dp[h + 1][w] %= MOD
        if w + 1 < W and a[h][w + 1] == ".":
            dp[h][w + 1] += dp[h][w]
            dp[h][w + 1] %= MOD

print(dp[-1][-1])
