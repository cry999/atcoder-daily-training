# ナップザックだろうなと思います。
N = int(input())
WHB = [tuple(map(int, input().split())) for _ in range(N)]
# print(*WHB)

MAX_WEIGHT = sum(map(lambda x: x[0], WHB)) // 2

# dp[i][j]: 部品 1, 2, 3, ... i を使って頭の重さが j 以下のものを作るときの最大価値
dp = [[0] * (MAX_WEIGHT+1) for _ in range(N+1)]

for i in range(1, N+1):
    w, h, b = WHB[i-1]
    for j in range(MAX_WEIGHT+1):
        dp[i][j] = max(
            dp[i-1][j] + b,  # 体に採用
            dp[i-1][j-w] + h if j-w >= 0 else 0,  # 頭に採用
        )

print(dp[N][MAX_WEIGHT])
