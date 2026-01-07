N, W = map(int, input().split())
# dp = [[0] * (W + 1) for _ in range(N + 1)]
dp = [0] * (W + 1)

for i in range(N):
    w, v = map(int, input().split())
    for ww in range(W, -1, -1):
        dp[ww] = max(dp[ww], dp[ww - w] + v if ww - w >= 0 else 0)
print(max(dp))
