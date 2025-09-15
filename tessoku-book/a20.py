S, T = input(), input()

dp = [[0] * (len(T)+1) for _ in range(len(S)+1)]
for i in range(len(S)):
    for j in range(len(T)):
        dp[i+1][j+1] = max(
            dp[i][j+1],
            dp[i+1][j],
            dp[i][j] + 1 if S[i] == T[j] else 0,
        )

print(dp[-1][-1])
# print(dp)
