from math import sqrt


N = int(input())
XY = [tuple(map(int, input().split())) for _ in range(N)]
dist = [[
    sqrt((x1-x2)**2 + (y1-y2)**2)
    for x1, y1 in XY
] for x2, y2 in XY]

dp = [[float('inf')] * (N) for _ in range(1 << N)]
dp[0][0] = 0

for i in range(1 << N):  # i: 訪れた都市の集合
    for j in range(N):  # j: 今いる都市
        for k in range(N):  # k: 次に行く都市
            if j == k:  # 同じ都市には行けない
                continue
            if i & (1 << k):  # k に訪れているとだめ
                continue
            dp[i | (1 << k)][k] = min(  # i に k を追加したときの最小値
                dp[i | (1 << k)][k],  # 現在の最小値
                dp[i][j] + dist[j][k],
            )
            pass

print(dp[(1 << N) - 1][0])
