N = int(input())
T = input()

# dp[i][0] := i 文字目を右端にもつ美しい部分文字列の個数
dp = [[0] * 2 for _ in range(N + 1)]

for i in range(N):
    n = int(T[i])
    dp[i + 1][n] = dp[i][1] + 1
    dp[i + 1][1 - n] = dp[i][0]

ans = sum(dp[i + 1][1] for i in range(N))
print(ans)
