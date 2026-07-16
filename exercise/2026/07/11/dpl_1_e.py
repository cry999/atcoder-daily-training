s1 = input()
n1 = len(s1)
s2 = input()
n2 = len(s2)

INF = 10**18
dp = [[INF] * (n2 + 1) for _ in range(n1 + 1)]
dp[0][0] = 0
for i in range(n1 + 1):
    for j in range(n2 + 1):
        if i + 1 <= n1:
            dp[i + 1][j] = min(dp[i + 1][j], dp[i][j] + 1)
        if j + 1 <= n2:
            dp[i][j + 1] = min(dp[i][j + 1], dp[i][j] + 1)
        if i + 1 <= n1 and j + 1 <= n2:
            if s1[i] == s2[j]:
                dp[i + 1][j + 1] = min(dp[i + 1][j + 1], dp[i][j])
            else:
                dp[i + 1][j + 1] = min(dp[i + 1][j + 1], dp[i][j] + 1)

print(dp[n1][n2])
