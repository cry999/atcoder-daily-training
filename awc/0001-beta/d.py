N, M, K = map(int, input().split())

dp = [[0] * (M + 1) for _ in range(N + 1)]
dp[0] = [0] * (M + 1)

for i in range(N):
    a, b = map(int, input().split())
    for m in range(b, M + 1):
        dp[i + 1][m] = max(dp[i + 1][m], a)

    for k in range(1, K + 1):
        if i + 1 - k < 0:
            break
        for m in range(M + 1):
            if m + b > M:
                break
            dp[i + 1][m + b] = max(dp[i + 1][m + b], dp[i + 1 - k][m] + a)

    for m in range(M):
        dp[i + 1][m + 1] = max(dp[i + 1][m + 1], dp[i + 1][m])

# print(dp)
ans = 0
for i in range(N + 1):
    for m in range(M + 1):
        ans = max(ans, dp[i][m])

print(ans)
