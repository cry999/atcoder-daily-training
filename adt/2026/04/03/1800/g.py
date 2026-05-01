N = int(input())
(*a,) = map(int, input().split())
(*b,) = map(int, input().split())

MOD = 998244353
M = 3000
# dp[i][j]: c[i] の値を j 以下にしたときの (c[1], ..., c[i]) の場合の数
dp = [[0] * (M + 1) for _ in range(N + 1)]
for j in range(M + 1):
    dp[0][j] = 1

for i in range(N):
    for j in range(a[i], b[i] + 1):
        dp[i + 1][j] = dp[i][j]

    for j in range(M):
        dp[i + 1][j + 1] += dp[i + 1][j]
        dp[i + 1][j + 1] %= MOD

print(dp[N][-1])
