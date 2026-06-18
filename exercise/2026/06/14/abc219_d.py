N = int(input())

INF = 10**9
X, Y = map(int, input().split())

lunchboxes = [tuple(map(int, input().split())) for _ in range(N)]

# dp[x][y] = X 個以上のたこ焼きと Y 個以上のたい焼きを手に入れるための最小のお弁当購入数
dp = [[INF] * (Y + 1) for _ in range(X + 1)]
dp[0][0] = 0

for a, b in lunchboxes:
    for x in range(X, -1, -1):
        for y in range(Y, -1, -1):
            dp[min(x + a, X)][min(y + b, Y)] = min(
                dp[min(x + a, X)][min(y + b, Y)],
                dp[x][y] + 1,
            )

print(dp[X][Y] if dp[X][Y] != INF else -1)
