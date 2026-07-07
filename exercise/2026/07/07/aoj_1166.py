ADJ = [(1, 0), (0, 1), (-1, 0), (0, -1)]
while True:
    W, H = map(int, input().split())
    if W == H == 0:
        break
    walls = []
    for _ in range(2 * H - 1):
        walls.append(list(map(int, input().split())))
    walls.append([0] * (W - 1))

    dist = [-1] * (H * W)

    q = [0]
    dist[0] = 0

    for p in q:
        h, w = divmod(p, W)
        for dh, dw in ADJ:
            nh, nw = h + dh, w + dw
            n = nh * W + nw
            if not (0 <= nh < H and 0 <= nw < W):
                continue
            if dw == 1 and walls[2 * h][w] == 1:
                # 右に壁がある
                continue
            elif dw == -1 and walls[2 * h][w - 1] == 1:
                # 左に壁がある
                continue
            elif dh == 1 and walls[2 * h + 1][w] == 1:
                # 下に壁がある
                continue
            elif dh == -1 and walls[2 * h - 1][w] == 1:
                # 下に壁がある
                continue

            if dist[n] != -1:
                # 訪問済み
                continue
            dist[n] = dist[p] + 1
            q.append(n)

    print(dist[H * W - 1] + 1)
