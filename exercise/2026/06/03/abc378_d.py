H, W, K = map(int, input().split())
S = [input() for _ in range(H)]


visited = set()

DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def dfs(h: int, w: int, step: int):
    # print(f"  dfs({h}, {w}, {step})")
    if step == K:
        # print(f"    found: {h}, {w}")
        return 1

    if S[h][w] == "#":
        # print(f"    wall: {h}, {w}")
        return 0

    ret = 0
    visited.add((h, w))

    for dh, dw in DIRS:
        nh, nw = h + dh, w + dw
        # print(f"    try go {dh}, {dw} to ({nh}, {nw})")

        if not (0 <= nh < H and 0 <= nw < W):
            # print(f"      out of range: {nh}, {nw}")
            continue
        if S[nh][nw] == "#":
            # print(f"      wall: {nh}, {nw}")
            continue
        if (nh, nw) in visited:
            # print(f"      already visited: {nh}, {nw}")
            continue
        ret += dfs(nh, nw, step + 1)

    visited.remove((h, w))
    return ret


ans = 0
for h in range(H):
    for w in range(W):
        # print(f"start from ({h}, {w})")
        ans += dfs(h, w, 0)
print(ans)
