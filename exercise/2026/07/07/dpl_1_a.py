N, M = map(int, input().split())
(*C,) = map(int, input().split())

dp = [float("inf")] * (N + 1)
dp[0] = 0

for c in C:
    for n in range(N - c + 1):
        dp[n + c] = min(dp[n + c], dp[n] + 1)
print(dp[N])
