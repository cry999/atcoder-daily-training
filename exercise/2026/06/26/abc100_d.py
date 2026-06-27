import sys

input = sys.stdin.readline

N, M = map(int, input().split())

INF = 10**18

dp = [[-INF] * 8 for _ in range(M + 1)]
for i in range(8):
    dp[0][i] = 0

for i in range(N):
    x, y, z = map(int, input().split())

    for m in range(M - 1, -1, -1):
        dp[m + 1][0] = max(dp[m + 1][0], dp[m][0] + x + y + z)
        dp[m + 1][1] = max(dp[m + 1][1], dp[m][1] + x + y - z)
        dp[m + 1][2] = max(dp[m + 1][2], dp[m][2] + x - y + z)
        dp[m + 1][3] = max(dp[m + 1][3], dp[m][3] + x - y - z)
        dp[m + 1][4] = max(dp[m + 1][4], dp[m][4] - x + y + z)
        dp[m + 1][5] = max(dp[m + 1][5], dp[m][5] - x + y - z)
        dp[m + 1][6] = max(dp[m + 1][6], dp[m][6] - x - y + z)
        dp[m + 1][7] = max(dp[m + 1][7], dp[m][7] - x - y - z)

print(max(map(abs, dp[M])))
