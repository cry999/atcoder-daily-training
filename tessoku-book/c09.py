N = int(input())
A = list(map(int, input().split()))

# dp[i] = i 日目の最大実力
dp = [0] * (N+1)
dp[1] = A[0]

for i in range(2, N+1):
    dp[i] = max(dp[i-2] + A[i-1], dp[i-1])

print(dp[N])
