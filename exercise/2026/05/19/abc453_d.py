import sys

sys.setrecursionlimit(10**7)


H, W = map(int, input().split())
S = [input() for _ in range(H)]

sh, sw = -1, -1
gh, gw = -1, -1
for h in range(H):
    for w in range(W):
        if S[h][w] == "S":
            sh, sw = h, w
        if S[h][w] == "G":
            gh, gw = h, w

T = []
visited = bytearray(H * W)
visited[sh * W + sw] = 0b1111

DIRS = [
    (-1, 0, 0, "U"),
    (1, 0, 1, "D"),
    (0, -1, 2, "L"),
    (0, 1, 3, "R"),
]


def dfs(h: int, w: int, pd: int = -1):
    # print(f"dfs({h}, {w}, {pdh}, {pdw})")
    if h == gh and w == gw:
        return True

    for dh, dw, i, c in DIRS:
        nh, nw = h + dh, w + dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "#":
            continue
        if S[h][w] == "o" and i != pd:
            # o にいるなら同じ方向にしか進めない
            continue
        if S[h][w] == "x" and i == pd:
            # x にいるなら同じ方向には進めない
            continue
        if visited[nh * W + nw] & (1 << i):
            continue
        if S[nh][nw] == "o" or S[nh][nw] == "x":
            visited[nh * W + nw] |= 1 << i
        else:
            visited[nh * W + nw] = 0b1111

        # print(f"  go {dir_str(dh, dw)} to ({nh}, {nw})")
        T.append(c)
        if dfs(nh, nw, i):
            return True
        T.pop()

    return False


if dfs(sh, sw):
    print("Yes")
    print("".join(T))
else:
    print("No")
