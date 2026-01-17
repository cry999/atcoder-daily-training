N = int(input())
(*A,) = map(int, input().split())

# N 本目を選択しないと決めた dp
dp = [[float("inf")] * 2 for _ in range(N)]
dp[0][1] = A[0]

for i in range(N - 1):
    dp[i + 1][0] = dp[i][1]
    dp[i + 1][1] = min(dp[i]) + A[i + 1]


ans = min(dp[-1])


# N 本目を選択すると決めた dp
dp = [[float("inf")] * 2 for _ in range(N)]
dp[0][1] = A[-1]

for i in range(N - 1):
    dp[i + 1][0] = dp[i][1]
    dp[i + 1][1] = min(dp[i]) + A[i]

ans = min(ans, min(dp[-1]))

print(ans)
