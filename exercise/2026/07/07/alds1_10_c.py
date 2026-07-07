import sys

input = sys.stdin.readline

Q = int(input())

for _ in range(Q):
    X = input().rstrip()
    Y = input().rstrip()
    LX, LY = len(X), len(Y)

    dp = [[0] * (LY + 1) for _ in range(LX + 1)]

    for i in range(LX + 1):
        for j in range(LY + 1):
            if i + 1 <= LX:
                dp[i + 1][j] = max(dp[i + 1][j], dp[i][j])
            if j + 1 <= LY:
                dp[i][j + 1] = max(dp[i][j + 1], dp[i][j])
            if i < LX and j < LY and X[i] == Y[j]:
                dp[i + 1][j + 1] = max(dp[i + 1][j + 1], dp[i][j] + 1)

    print(dp[LX][LY])
