N, K = map(int, input().split())
(*h,) = map(int, input().split())

dp = [float("inf")] * N
dp[0] = 0
for i in range(N):
    for k in range(1, K + 1):
        if i + k >= N:
            break
        dp[i + k] = min(dp[i + k], dp[i] + abs(h[i + k] - h[i]))

print(dp[N - 1])
