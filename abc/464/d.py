T = int(input())

SUNNY = 0
RAINY = 1

for _ in range(T):
    N = int(input())
    S = input()
    (*X,) = map(int, input().split())
    (*Y,) = map(int, input().split())

    # dp[i][j] := i日目までの天候を操作して、i日目が RAINY or SUNNY である時の嬉しさ最大値
    dp = [[0] * 2 for _ in range(N + 1)]
    dp[1][SUNNY] = 0 if S[0] == "S" else -X[0]
    dp[1][RAINY] = 0 if S[0] == "R" else -X[0]

    for i in range(1, N):
        if S[i] == "S":
            # 天候を操作しない
            dp[i + 1][SUNNY] = max(dp[i][SUNNY], dp[i][RAINY] + Y[i - 1])
            # 天候を操作する
            dp[i + 1][RAINY] = max(dp[i]) - X[i]
        else:
            # 天候を操作しない
            dp[i + 1][RAINY] = max(dp[i])
            # 天候を操作する
            dp[i + 1][SUNNY] = max(dp[i][SUNNY], dp[i][RAINY] + Y[i - 1]) - X[i]

    print(max(dp[N]))
