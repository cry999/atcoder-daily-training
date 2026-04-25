H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]
(*P,) = map(int, input().split())

B = [[0] * W for _ in range(H)]

for i in range(H):
    for j in range(W):
        B[i][j] = A[i][j] - P[i + j]

dp = [[float("inf")] * W for _ in range(H)]
dp[H - 1][W - 1] = 0

for i in range(H - 1, -1, -1):
    for j in range(W - 1, -1, -1):
        if i + 1 < H:
            dp[i][j] = min(dp[i][j], dp[i + 1][j])
        if j + 1 < W:
            dp[i][j] = min(dp[i][j], dp[i][j + 1])

        dp[i][j] = max(0, dp[i][j] - B[i][j])

print(dp[0][0])
