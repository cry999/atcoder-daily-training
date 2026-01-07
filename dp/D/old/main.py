N, W = map(int, input().split())
dp = [-float("inf")] * (W + 1)
dp[0] = 0

for _ in range(N):
    w, v = map(int, input().split())
    for i in range(W, w - 1, -1):
        dp[i] = max(dp[i], dp[i - w] + v)
print(max(dp))
