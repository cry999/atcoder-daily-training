import sys

input = sys.stdin.readline


H, W, C = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]

INF = 10**18

min_cost = [INF] * (H * W)
ans = INF

# 左上と右下の関係
for p in range(H * W):
    i, j = divmod(p, W)
    ans = min(ans, min_cost[p] + A[i][j] + C * (i + j))
    if j + 1 < W:
        min_cost[p + 1] = min(
            min_cost[p + 1],
            min_cost[p],
            A[i][j] - C * (i + j),
        )
    if i + 1 < H:
        min_cost[p + W] = min(
            min_cost[p + W],
            min_cost[p],
            A[i][j] - C * (i + j),
        )

for p in range(H * W):
    min_cost[p] = INF

# 右上と左下の関係
for p in range(H * W):
    i, j = divmod(p, W)
    j = W - j - 1
    q = i * W + j
    ans = min(ans, min_cost[q] + A[i][j] + C * (i - j))
    if j - 1 >= 0:
        min_cost[q - 1] = min(
            min_cost[q - 1],
            min_cost[q],
            A[i][j] - C * (i - j),
        )
    if i + 1 < H:
        min_cost[q + W] = min(
            min_cost[q + W],
            min_cost[q],
            A[i][j] - C * (i - j),
        )

print(ans)
