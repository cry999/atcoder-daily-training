N = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))

dp = [0] * (N+1)

for i in range(N-1, 0, -1):
    dp[i] = max(dp[A[i-1]]+100, dp[B[i-1]]+150)

print(dp[1])
