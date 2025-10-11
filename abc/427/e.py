H, W = map(int, input().split())
A = [input() for _ in range(H)]

sx, sy = -1, -1
for i in range(H):
    for j in range(W):
        if A[i][j] == 'T':
            sx, sy = i, j
            break

# 2 次元累積和
# s[i][j] := (0,0) から (i-1,j-1) までの '#' (ゴミ)の個数
s = [[0] * (W+1) for _ in range(H+1)]
for i in range(H):
    for j in range(W):
        s[i+1][j+1] = s[i+1][j] + s[i][j+1] - s[i][j] + (A[i][j] == '#')

# dp[lx][rx][ly][ry][dx][dy] = lx <= x < rx かつ ly <= y < ry を満たす (x, y) に
# ゴミがあって、(x+dx, y+dy) にゴミがある状態までの距離
dp = [
    [
        [
            [
                [
                    [float('inf')] * (2*W+1)
                    for _ in range(2*H+1)
                ] for _ in range(W+1)
            ] for _ in range(W+1)
        ] for _ in range(H+1)
    ] for _ in range(H+1)
]

dp[0][H][0][W][H][W] = 0
queue = [(0, H, 0, W, H, W)]

while queue:
    lx, rx, ly, ry, dx, dy = queue.pop(0)
    if s[rx][ry] + s[lx][ly] - s[lx][ry] - s[rx][ly] == 0:
        # ゴミが片付いた
        print(dp[lx][rx][ly][ry][dx][dy])
        break
    # 4 方向に移動する
    for ndx, ndy in [(dx-1, dy), (dx+1, dy), (dx, dy-1), (dx, dy+1)]:
        nlx, nrx = max(lx, ndx-H), min(rx, ndx)
        nly, nry = max(ly, ndy-W), min(ry, ndy)

        if ndx < 0 or 2*H < ndx or ndy < 0 or 2*W < ndy:
            continue
        x, y = sx + ndx - H, sy + ndy - W
        if nlx <= x and x < nrx and nly <= y and y < nry and A[x][y] == '#':
            # 高橋くんの位置にゴミがあるのでスキップ
            continue
        if dp[nlx][nrx][nly][nry][ndx][ndy] < float('inf'):
            # すでに訪問済み
            continue
        dp[nlx][nrx][nly][nry][ndx][ndy] = dp[lx][rx][ly][ry][dx][dy] + 1
        queue.append((nlx, nrx, nly, nry, ndx, ndy))
else:
    print(-1)
