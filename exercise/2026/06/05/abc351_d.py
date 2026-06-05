H, W = map(int, input().split())
S = [input() for _ in range(H)]

visited = [-1] * (H * W)
magnets = [False] * (H * W)

NEIGHBORS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


for pos in range(H * W):
    i, j = divmod(pos, W)
    if S[i][j] == "#":
        for di, dj in NEIGHBORS:
            ni, nj = i + di, j + dj
            if not (0 <= ni < H and 0 <= nj < W):
                continue
            magnets[ni * W + nj] = True

ans = 1
for pos in range(H * W):
    i, j = divmod(pos, W)
    if S[i][j] == "#":
        continue
    if magnets[pos]:
        continue
    if visited[pos] >= 0:
        continue
    visited[pos] = pos

    stack = [pos]
    res = 0

    while stack:
        cur = stack.pop()
        res += 1
        if magnets[cur]:
            continue

        ci, cj = divmod(cur, W)
        for di, dj in NEIGHBORS:
            ni, nj = ci + di, cj + dj
            if not (0 <= ni < H and 0 <= nj < W):
                continue
            nxt = ni * W + nj
            if visited[nxt] == pos:
                continue
            visited[nxt] = pos
            stack.append(nxt)

    ans = max(ans, res)


print(ans)
