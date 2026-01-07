N, K = map(int, input().split())
(*h,) = map(int, input().split())

dp = [float("inf")] * N
dp[0] = 0
for i in range(N):
    for k in range(i + 1, min(i + K + 1, N)):
        dp[k] = min(dp[k], dp[i] + abs(h[k] - h[i]))
print(dp[-1])
