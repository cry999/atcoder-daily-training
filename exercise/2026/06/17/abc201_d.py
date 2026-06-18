H, W = map(int, input().split())
A = [input() for _ in range(H)]
B = [[1 if A[h][w] == "+" else -1 for w in range(W)] for h in range(H)]

dp = [[0] * W for _ in range(H)]

for h in range(H - 1, -1, -1):
    for w in range(W - 1, -1, -1):
        if h + 1 < H and w + 1 < W:
            dp[h][w] = max(B[h + 1][w] - dp[h + 1][w], B[h][w + 1] - dp[h][w + 1])
        elif h + 1 < H:
            dp[h][w] = B[h + 1][w] - dp[h + 1][w]
        elif w + 1 < W:
            dp[h][w] = B[h][w + 1] - dp[h][w + 1]

if dp[0][0] > 0:
    print("Takahashi")
elif dp[0][0] < 0:
    print("Aoki")
else:
    print("Draw")
