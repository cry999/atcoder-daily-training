s = input()
t = input()

dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]

for i in range(len(s) + 1):
    for j in range(len(t) + 1):
        if i < len(s):
            dp[i + 1][j] = max(dp[i + 1][j], dp[i][j])
        if j < len(t):
            dp[i][j + 1] = max(dp[i][j + 1], dp[i][j])
        if i < len(s) and j < len(t) and s[i] == t[j]:
            dp[i + 1][j + 1] = max(dp[i + 1][j + 1], dp[i][j] + 1)

cur = (len(s), len(t))
ans = ""

while cur != (0, 0):
    i, j = cur
    if i > 0 and dp[i - 1][j] == dp[i][j]:
        cur = (i - 1, j)
        continue
    if j > 0 and dp[i][j - 1] == dp[i][j]:
        cur = (i, j - 1)
        continue
    ans += s[i - 1]
    cur = (i - 1, j - 1)

print(ans[::-1])
