S, T = input(), input()

dp = [[0] * (len(T)+1) for _ in range(len(S)+1)]
for i in range(len(S)+1):
    dp[i][0] = i
for i in range(len(T)+1):
    dp[0][i] = i

for i in range(1, len(S)+1):
    for j in range(1, len(T)+1):
        dp[i][j] = min(
            dp[i-1][j] + 1,
            dp[i][j-1] + 1,
            dp[i-1][j-1] + (S[i-1] != T[j-1])
        )

print(dp[-1][-1])
