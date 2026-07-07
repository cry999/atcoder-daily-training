import sys

sys.setrecursionlimit(10**6)

ADJ = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]
while True:
    W, H = map(int, input().split())
    if W == H == 0:
        break

    C = [list(map(int, input().split())) for _ in range(H)]
    visited = [False] * (W * H)
    islands = 0

    def dfs(h: int, w: int):
        visited[h * W + w] = True
        for dh, dw in ADJ:
            nh, nw = h + dh, w + dw
            if not (0 <= nh < H and 0 <= nw < W):
                continue
            if visited[nh * W + nw]:
                continue
            if C[nh][nw] == 0:
                continue
            dfs(nh, nw)

    for pos in range(H * W):
        h, w = divmod(pos, W)
        if visited[pos]:
            continue
        if C[h][w] == 0:
            continue
        islands += 1
        dfs(h, w)

    print(islands)
