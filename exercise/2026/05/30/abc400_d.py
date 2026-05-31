from collections import deque

H, W = map(int, input().split())
S = [input() for _ in range(H)]

A, B, C, D = map(lambda x: int(x) - 1, input().split())

# wall は壁を壊した回数を表す。同じ位置でも壁を壊す回数が少なく到達できる方を優先する。
# 優先度としては、壁を壊す回数が少ないことが 1 点目、次に到達までの移動回数が少ないこと。
wall = [[-1] * W for _ in range(H)]

q = deque()
q.append((A, B, 0, 0, -1))

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

while q:
    # d: 移動回数, c: 壁を壊した回数, p: 前回すでに壊した壁の方向(DIRS の index)
    h, w, d, c, p = q.popleft()
    # print(f"({h}, {w}), d={d}, c={c}")

    for i, (dh, dw) in enumerate(DIRS):
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue

        if S[nh][nw] == ".":
            if 0 <= wall[nh][nw] <= c:
                continue
            wall[nh][nw] = c
            q.appendleft((nh, nw, d + 1, c, -1))
        elif i == p:  # wall
            if 0 <= wall[nh][nw] <= c:
                continue
            wall[nh][nw] = c
            q.appendleft((nh, nw, d + 1, c, -1))
        else:
            if 0 <= wall[nh][nw] <= c + 1:
                continue
            wall[nh][nw] = c + 1
            q.append((nh, nw, d + 1, c + 1, i))

print(wall[C][D])
