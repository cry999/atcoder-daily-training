W, H = map(int, input().split())
S = [
    (
        [0] * (W + 2)
        if h == 0 or h == H + 1
        else [0] + list(map(int, input().split())) + [0]
    )
    for h in range(H + 2)
]

visited = [False] * ((H + 2) * (W + 2))

ADJ = [
    # 偶数行の遷移
    [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)],
    # 奇数行の遷移
    [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)],
]


wall = 0
for pos in range((H + 2) * (W + 2)):
    h, w = divmod(pos, W + 2)
    if h != 0 and h != H + 1 and w != 0 and w != W + 1:
        # 外周からだけ調査する。
        continue
    if visited[pos]:
        continue
    visited[pos] = True

    q = [pos]
    for p in q:
        h, w = divmod(p, W + 2)
        for dh, dw in ADJ[h % 2]:
            nh, nw = h + dh, w + dw
            n = nh * (W + 2) + nw
            if not (0 <= nh < H + 2 and 0 <= nw < W + 2):
                continue
            if S[nh][nw] == 1:
                wall += 1
                continue

            # S[nh][nw] == 0
            if visited[n]:
                continue
            visited[n] = True
            q.append(n)
print(wall)
