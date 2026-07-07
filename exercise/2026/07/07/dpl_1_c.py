N, W = map(int, input().split())
dp = [-float("inf")] * (W + 1)
dp[0] = 0

for i in range(N):
    v, w = map(int, input().split())
    for x in range(W - w + 1):
        dp[x + w] = max(dp[x + w], dp[x] + v)
print(max(dp))
