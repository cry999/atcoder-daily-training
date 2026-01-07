s = input()
t = input()

len_s = len(s)
len_t = len(t)

dp = [[0] * (len_t + 1) for _ in range(len_s + 1)]
for i in range(len_s):
    for j in range(len_t):
        dp[i + 1][j + 1] = max(
            dp[i][j + 1],
            dp[i + 1][j],
            dp[i][j] + 1 if s[i] == t[j] else 0,
        )

ans = ""
i, j = len_s, len_t
while i and j:
    if i and j and dp[i][j] - 1 == dp[i - 1][j - 1] == dp[i - 1][j] == dp[i][j - 1]:
        ans += s[i - 1]
        i, j = i - 1, j - 1
    elif i and dp[i][j] == dp[i - 1][j]:
        i -= 1
    else:
        j -= 1
print(ans[::-1])
