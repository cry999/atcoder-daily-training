N, M = map(int, input().split())
(*X,) = map(int, input().split())
bonus = [0] * (N + 1)

for _ in range(M):
    c, y = map(int, input().split())
    bonus[c] = y

dp = [[0] * (N + 1) for _ in range(N + 1)]
for n in range(1, N + 1):
    x = X[n - 1]
    dp[n][0] = max(dp[n - 1])
    for c in range(1, n + 1):
        dp[n][c] = max(
            dp[n - 1][c],
            dp[n - 1][c - 1] + x + bonus[c] if c > 0 else 0,
        )

print(max(dp[-1]))
