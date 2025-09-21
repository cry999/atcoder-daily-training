# A16 と同じ

N = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))

dp = [float('inf')] * (N+1)
dp[1] = 0

for i in range(1, N-1):
    dp[i+1] = min(dp[i] + A[i-1], dp[i+1])
    dp[i+2] = min(dp[i] + B[i-1], dp[i+2])

dp[N] = min(dp[N], dp[N-1] + A[N-2])

# print(dp)
print(dp[N])
