N = int(input())
(*A,) = map(int, input().split())

dp = {}

ans = 0
for i in range(N):
    dp[A[i]] = max(dp.get(A[i], 1), dp.get(A[i] - 1, 0) + 1)
    ans = max(ans, dp[A[i]])

print(ans)
