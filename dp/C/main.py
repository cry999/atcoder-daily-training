N = int(input())
dp = [[0] * 3 for _ in range(N + 1)]

for i in range(N):
    (*a,) = map(int, input().split())
    dp[i + 1] = [max(dp[i][(j + 1) % 3], dp[i][(j + 2) % 3]) + a[j] for j in range(3)]
print(max(dp[-1]))
