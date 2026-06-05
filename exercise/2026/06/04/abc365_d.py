N = int(input())
s = input()

# dp[i][j] := i 回の勝負を終えて、最後に j を出した時の最大勝ち数
dp = [[-float("inf")] * 3 for _ in range(N + 1)]
for i in range(3):
    dp[0][i] = 0

R = 0
P = 1
S = 2

for i in range(N):
    if s[i] == "R":
        dp[i + 1][R] = max(dp[i][P], dp[i][S])
        dp[i + 1][P] = max(dp[i][R], dp[i][S]) + 1
    elif s[i] == "P":
        dp[i + 1][P] = max(dp[i][R], dp[i][S])
        dp[i + 1][S] = max(dp[i][R], dp[i][P]) + 1
    else:
        dp[i + 1][S] = max(dp[i][R], dp[i][P])
        dp[i + 1][R] = max(dp[i][P], dp[i][S]) + 1

print(max(dp[N]))
