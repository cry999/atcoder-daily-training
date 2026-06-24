N = int(input())
(*A,) = map(int, input().split())

# dp[i][0] = i 番目までの要素の処遇を決定。0 = i 番目をフリップしない。1 = i 番目をフリップする。
dp = [[0] * 2 for _ in range(N)]
dp[0][0] = A[0]
dp[0][1] = -A[0]

for i in range(N - 1):
    dp[i + 1][0] = max(dp[i][0] + A[i + 1], dp[i][1] - A[i + 1])
    dp[i + 1][1] = max(dp[i][0] - A[i + 1], dp[i][1] + A[i + 1])

# 最後はフリップできないので
print(dp[N - 1][0])
