N = int(input())
S = input()

dp = [[0] * (N) for _ in range(N)]
for i in range(N):
    dp[i][i] = 1
for i in range(N-1):
    if S[i] == S[i+1]:
        dp[i][i+1] = 2
    else:
        dp[i][i+1] = 1

for length in range(2, N):
    for i in range(N-length):
        j = i + length  # i から長さ length の部分文字列
        if S[i] == S[j]:
            dp[i][j] = dp[i+1][j-1] + 2
        else:
            dp[i][j] = max(dp[i+1][j], dp[i][j-1])

print(dp[0][N-1])
