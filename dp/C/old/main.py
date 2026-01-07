N = int(input())
dp = [[0] * 3 for _ in range(2)]

for i in range(N):
    (*scores,) = map(int, input().split())
    for j in range(3):
        dp[(i + 1) % 2][j] = max(
            dp[i % 2][(j + 1) % 3] + scores[j],
            dp[i % 2][(j + 2) % 3] + scores[j],
        )
    # print(i + 1, dp[(i + 1) % 2])

print(max(dp[N % 2]))
