N = int(input())
*A, = map(int, input().split())

dp = [[0]*2 for _ in range(N+1)]
dp[0][1] = -float('inf')
dp[1][0] = -float('inf')
dp[1][1] = A[0]

for i in range(2, N+1):
    dp[i][0] = max(dp[i-1][1], dp[i-2][1])+2*A[i-1]
    dp[i][1] = max(dp[i-1][0], dp[i-2][0])+A[i-1]

# print([dp[i][0] for i in range(N)])
# print([dp[i][1] for i in range(N)])
print(max(dp[N]))
