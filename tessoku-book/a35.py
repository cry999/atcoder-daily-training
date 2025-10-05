N = int(input())
A = list(map(int, input().split()))

# dp[i][j] := (i, j) をスタートとした時のスコア
# i % 2 == 0: dp[i][j] = max(dp[i+1][j], dp[i+1][j+1])
# i % 2 == 1: dp[i][j] = min(dp[i+1][j], dp[i+1][j+1])
dp = [[-1] * N for _ in range(N)]

dp[-1] = A[:]
for i in range(N-2, -1, -1):
    for j in range(i+1):
        if i % 2 == 0:
            dp[i][j] = max(dp[i+1][j], dp[i+1][j+1])
        else:
            dp[i][j] = min(dp[i+1][j], dp[i+1][j+1])

print(dp[0][0])
